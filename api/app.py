from core.responses import *
from core.sounds_like import sounds_like
from core.spotify_track_downloader import SpotifyTrackDownloader
import boto3
import core.settings as settings
import json
import logging
import os
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TRACK_ID_PARAM = "trackId"
DYNAMO_HASH = settings.DYNAMODB_TABLE_HASH_KEY
DYNAMO_SORT = settings.DYNAMODB_TABLE_SORT_KEY
BUCKET_NAME = settings.AUDIO_UPLOAD_BUCKET
FEATURE_COL = settings.FEATURE_COL

TABLE_NAME = settings.DYNAMODB_TABLE
region = os.getenv("REGION", "eu-west-1")
logger.info(f"Table_name: {TABLE_NAME}")
logger.info(f"Region: {region}")


def track_id_specified(params):
    ''' Check if a trackId parameter has been passed.

    Parameters:
    -----------
    params:
        dict, queryStringParameters of triggering event, can be None.

    returns:
        boolean, whether or not a parameter named `trackId` was passed.
    '''
    try:
        if params is None or params[TRACK_ID_PARAM] is None:
            logger.info("No trackId passed.")
            return False
        else:
            return True
    except KeyError:
        return False


def fetch_item_from_db(hash_key, sort_key='spotify'):
    ''' Fetch a single item from the database by hash key.
    '''
    # TODO: Refactor this to use a DynamoDB object.
    try:
        dynamodb = boto3.resource("dynamodb", region_name=region)
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(
            Key={
                DYNAMO_HASH: hash_key,
                DYNAMO_SORT: sort_key
            }
        )
        return response['Item']

    except KeyError:
        return False


def put(event, context, downloader=None):
    ''' Function to handle HTTP PUT requests.

    The `downloader` parameter exists to enable dependency injection
    of a mock object to test this function's behaviour.
    '''
    if not track_id_specified(event["queryStringParameters"]):
        logger.info("trackId parameter not specified, returning 400.")
        return response_400(event)

    track_id = event["queryStringParameters"][TRACK_ID_PARAM]
    logger.info(f"track_id: {track_id}")

    item = fetch_item_from_db(track_id)
    if item:
        logger.info(f"Item with id {track_id} already exists, returning 200.")
        return response_200_put_exists(event, track_id, item)

    if not downloader:
        downloader = SpotifyTrackDownloader(BUCKET_NAME, track_id)

    downloaded = downloader.download_track()
    if downloaded == False:
        logger.info("No preview available or invalid id, returning 204.")
        return response_204(event, track_id)

    elif downloaded == True:
        logger.info("Preview uploaded to S3, returning 202.")
        return response_202(event, track_id)

    else:
        logger.warning("Unexpected response from downloader, returning 500.")
        return response_500(event)



def get(event, context):
    ''' Function to handle HTTP GET requests.
    '''
    if not track_id_specified(event["queryStringParameters"]):
        return response_400(event)

    track_id = event["queryStringParameters"][TRACK_ID_PARAM]
    logger.info(f"Checking for TrackId=={track_id} in database...")
    item = fetch_item_from_db(track_id)

    if not item:
        logger.info(f"TrackId=={track_id} not in database, returning 404.")
        return response_404(event, track_id)
    else:
        results = sounds_like(
            track_id, TABLE_NAME, DYNAMO_HASH, FEATURE_COL)
        logger.info(f"Got sounds like results for {track_id}, returning 200.")
        return response_200_get_success(event, track_id, json.loads(results))


# Main function left in for debugging why recommendations are rubbish.
if __name__ == '__main__':
    # Default query id is for 'Foo Fighters - Everlong'
    query = "07q6QTQXyPRCf7GbLakRPr"
    if len(sys.argv) == 1:
        logger.info(f"Querying with default track id {query}...")
    else:
        query = sys.argv[1]
    event = {"queryStringParameters": {"trackId": query}}
    json = get(event, None)
    print(json)
