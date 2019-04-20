from annoy import AnnoyIndex
from boto3.dynamodb.types import Binary
from functools import partial
import boto3
import core.settings as settings
import json
import logging
import numpy as np
import pickle
import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

N = 10
N_TREES = settings.N_TREES
D = 100000
SEARCH_K = N_TREES * N * D


def deserialise_features(features):
    if isinstance(features, Binary):
        return pickle.loads(features.value, encoding="latin1")
    else:
        raise TypeError(
            f"Expected features with type Binary, got {type(features)}.")


def fetch_annoy_space():
    ''' Fetch annoy file from s3 and return annoy_space.
    '''
    dl_loc = '/tmp/annoy.ann'
    bucket = settings.ANNOY_BUCKET_NAME
    file = settings.ANNOY_FILE_NAME
    ordinality = settings.ANNOY_VECTOR_LENGTH
    logger.info(f"Vector length: {ordinality}")

    client = boto3.client('s3')
    logger.info(f"Downloading {file} from S3 bucket {bucket}...")
    client.download_file(bucket, file, dl_loc)

    logger.info(f"Loading retrieved {file}...")
    annoy_space = AnnoyIndex(ordinality, metric="angular")
    annoy_space.load(dl_loc)

    return annoy_space


def sounds_like(table, query_item, dyanmo_annoy_index_name, annoy_col_name):
    ''' Sounds like search using the given query track id.

    This function requires that the value of `track_id` be one that
    exists in the spot-rec database.

    Parameters:
    -----------
    table:
        core.DynamoTable, from which to get tracks by ANNOY index.

    query_item:
        string, json representation of the query document from DynamoDB.

    dyanmo_annoy_index_name:
        string, the name of the ANNOY index of the DynamoDB table.

    annoy_col_name
        string, the name of the ANNOY id column in DynamoDB.

    Returns:
    --------
        string, json representation of the retrieved tracks.
    '''
    logger.setLevel(logging.DEBUG)
    query_id = query_item['TrackId']
    logger.info(f"Table: {table}")
    logger.info(f"Query id: {query_id}")
    logger.info(f"DynamoDB index name: {dyanmo_annoy_index_name}")
    logger.info(f"DyanmoDB ANNOY column: {annoy_col_name}")

    annoy_space = fetch_annoy_space()
    logger.info(f"Fetching near neighbours for query {query_id}...")
    vector = deserialise_features(query_item[settings.DYNAMO_ANNOY_VECTOR_COL])
    (nn_indices, dists) = annoy_space.get_nns_by_vector(
        vector, N, search_k=SEARCH_K, include_distances=True)

    # logger.debug(f"Query index: {annoy_index}")
    logger.debug(f"Neighbour indices: {nn_indices}")
    logger.debug(f"Neighbour distances: {dists}")

    get_annoy_track = partial(
        table.get_item_from_index,
        dyanmo_annoy_index_name,
        annoy_col_name
    )

    tracks = [json.dumps(get_annoy_track(nn)) for nn in nn_indices]
    return f"[{','.join(tracks)}]"
