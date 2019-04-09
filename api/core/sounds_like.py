from annoy import AnnoyIndex
import boto3
import core.settings as settings
import json
import logging
import pickle
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

N = 10
N_TREES = settings.N_TREES
D = 100000
SEARCH_K = N_TREES * N * D


def fetch_annoy_index():
    ''' Fetch annoy file from s3 and return index.
    '''
    dl_loc = '/tmp/annoy.ann'
    bucket = settings.ANNOY_BUCKET_NAME
    file = settings.ANNOY_FILE_NAME
    index_ordinality = settings.ANNOY_VECTOR_LENGTH

    client = boto3.client('s3')
    client.download_file(bucket, file, dl_loc)

    index = AnnoyIndex(index_ordinality)
    index.load(dl_loc)

    return index


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

    index = fetch_annoy_index()

    # Get near neighbours
    query_idx = df[hash_key][df[hash_key] == track_id].index[0]
    (nn_indices, dists) = index.get_nns_by_item(
        query_idx, N, search_k=SEARCH_K, include_distances=True)

    # logger.setLevel(logging.DEBUG)
    logger.debug(f"Query index: {query_idx}")
    logger.debug(f"Neighbour indices: {nn_indices}")
    logger.debug(f"Neighbour distances: {dists}")

    filtered = df[df.index.isin(nn_indices)]
    logger.info(f"Filtered shape: {filtered.shape}")
    filtered['Distance'] = dists

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
