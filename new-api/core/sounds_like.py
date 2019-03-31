from annoy import AnnoyIndex
from boto3.dynamodb.types import Binary
from core.dataframe_constructor import DataFrameConstructor
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import json
import logging
import numpy as np
import pandas as pd
import pickle
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

N = 10
N_TREES = 128
D = 100000
SEARCH_K = N_TREES * N * D
METRIC = "angular"


# TODO: Investigate if working properly, unit and integration tests.
def deserialise_features(features):
    try:
        return pickle.loads(
            bytes(features, encoding="ASCII"),
            encoding="latin1"
        )
    except TypeError:
        # Features are already bytes.
        # TODO: Ensure features are always bytes and update this method.
        if isinstance(features, Binary):
            return pickle.loads(features.value, encoding="latin1")
        else:
            raise TypeError(
                f"Expected string or Binary, got {type(features)}.")


def process_features(features, target_variance=0.95):
    ''' Deserialise, normalise, and perform PCA projection.

    Parameters:
    -----------
    features:
        pandas.Series, each item in the series is an ASCII pickled
        numpy.ndarray feature vector.

    target_variance:
        float, the target proportion of variance to retian in PCA projection.

    Returns:
    --------
        pandas.DataFrame, design matrix of processed features.
    '''
    logger.info(f"Processing features...")

    df_feats = pd.DataFrame(
        {i: deserialise_features(s)
         for i, s in features.iteritems()}
    ).T

    # Scale to zero mean, unit variance
    scaler = StandardScaler()
    norm_feats = scaler.fit_transform(df_feats)

    # Fit PCA
    pca = PCA()
    pca.fit_transform(norm_feats)

    # Fit d to target variance
    d = 1
    while np.sum(pca.explained_variance_ratio_[:d]) < target_variance:
        d += 1

    logger.info(f"Projecting features to {d} dimensions...")
    projection = [norm_feats.dot(pca.components_[i]) for i in range(d)]
    np_projection = np.array(projection).T

    logger.info(f"Returning projection with shape {np_projection.shape}...")
    return pd.DataFrame(np_projection)


def sounds_like(track_id, table_name, hash_key, feature_col):
    ''' Sounds like search using the given query track id.

    This function requires that the value of `track_id` be one that
    exists in the spot-rec database.

    Parameters:
    -----------
    track_id:
        string, the (Spotify) track id of the query song.

    Returns:
    --------
        string, json representation of the retrieved tracks.
    '''
    logger.setLevel(logging.DEBUG)

    # Get all metadata and features.
    df = DataFrameConstructor(table_name, hash_key).get_dataframe()
    projection = process_features(df[feature_col])

    # Build ANNOY space
    vector_len = projection.shape[1]
    logger.info(f"Creating ANNOY space for vectors of length {vector_len}...")
    index = AnnoyIndex(vector_len, metric=METRIC)

    for i, val in projection.iterrows():
        index.add_item(i, val.to_numpy())

    logger.info(f"Building ANNOY space with {N_TREES} trees...")
    index.build(N_TREES)

    # Get near neighbours
    query_idx = df[hash_key][df[hash_key] == track_id].index[0]
    (nn_indices, dists) = index.get_nns_by_item(
        query_idx, N, search_k=SEARCH_K, include_distances=True)

    filtered = df.iloc[nn_indices]
    filtered['Distance'] = dists

    # logger.setLevel(logging.DEBUG)
    logger.debug(f"Query index: {query_idx}")
    logger.debug(f"Neighbour indices: {nn_indices}")
    logger.debug(f"Neighbour distances: {dists}")

    return filtered.drop(
        [feature_col], axis=1).to_json(orient='records')


if __name__ == '__main__':
    # Default query id is for 'Foo Fighters - Everlong'
    query = "07q6QTQXyPRCf7GbLakRPr"
    if len(sys.argv) == 1:
        logger.info(f"Querying with default track id {query}...")
    else:
        query = sys.argv[1]
    table_name = "spot-rec-audio-metadata"
    hash_key = "TrackId"
    feature_col = "Features"
    json = sounds_like(query, table_name, hash_key, feature_col)
    print(json)
