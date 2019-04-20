import boto3
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def __get_parameter(name):
    if not name or name == "":
        raise ValueError("name not passed.")

    system_code = "spot-rec"
    name = f"/{system_code}/{name}"
    client = boto3.client('ssm')
    response = client.get_parameter(Name=name)
    return response ['Parameter']['Value']


# Refactor to get from env vars.
client_id = __get_parameter('shared/client_id')
client_secret = __get_parameter('shared/client_secret')
DYNAMODB_TABLE_HASH_KEY = __get_parameter('dynamodb_hash_key_name')
DYNAMODB_TABLE_SORT_KEY = __get_parameter('dynamodb_sort_key_name')
AUDIO_UPLOAD_BUCKET = __get_parameter('audio_bucket_name')
FEATURE_COL = __get_parameter('feature_column_name')
FEATURE_VECTOR_LENGTH = int(__get_parameter('feature_vector_length'))
ANNOY_INDEX_COL = __get_parameter('annoy_index_col_name')

DYNAMODB_TABLE = os.getenv("TRACKS_TABLE", None)
ANNOY_BUCKET_NAME = os.getenv("ANNOY_BUCKET_NAME", None)
ANNOY_FILE_NAME = os.getenv("ANNOY_FILE_NAME", None)
ANNOY_VECTOR_LENGTH = os.getenv("ANNOY_VECTOR_LENGTH", 93)
N_TREES = os.getenv("N_TREES", 128)
DYNAMO_ANNOY_INDEX_NAME = os.getenv("DYNAMO_ANNOY_INDEX_NAME", None)
DYNAMO_ANNOY_VECTOR_COL = os.getenv("DYNAMO_ANNOY_VECTOR_COL", "AnnoyVector")

if not DYNAMODB_TABLE:
    logger.critical("DyanmoDB table name not set, cannot continue.")
    exit(1)

if not DYNAMO_ANNOY_INDEX_NAME:
    logger.critical("DyanmoDB ANNOY index name not set, cannot continue.")
    exit(1)

if not ANNOY_BUCKET_NAME:
    logger.critical("ANNOY bucket name not set, cannot continue.")
    exit(1)

if not ANNOY_FILE_NAME:
    logger.critical("ANNOY file name not set, cannot continue.")
    exit(1)
