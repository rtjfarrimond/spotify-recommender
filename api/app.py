from core.spotify_track_downloader import SpotifyTrackDownloader
from core.responses import *
import boto3
import json
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TRACK_ID_PARAM = "trackId"
DYNAMO_PK = "TrackId" # TODO: put this in ssm
BUCKET_NAME = "spot-rec-audio-upload-bucket" # TODO: put this in ssm

# TODO: Put table_name in SSM with serverless then fetch from there.
table_name = os.getenv("TRACKS_TABLE", "spot-rec-api-dev-dynamodb")
region = os.getenv("REGION", "eu-west-1")
logger.info(f"table_name: {table_name}")
logger.info(f"region: {region}")

# Get an instance of the dynamodb table.
dynamodb = boto3.resource("dynamodb", region_name=region)
table = dynamodb.Table(table_name)


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

def put(event, context, downloader=None):
    ''' Function to handle PUT requests.

    The `downloader` parameter exists to enable dependency injection
    of a mock object to test this function's behaviour.
    '''
    if not track_id_specified(event["queryStringParameters"]):
        logger.info("trackId parameter not specified, returning 400.")
        return response_400(event)

    track_id = event["queryStringParameters"][TRACK_ID_PARAM]
    logger.info(f"track_id: {track_id}")

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
    if not track_id_specified(event["queryStringParameters"]):
        return response_400(event)

    track_id = event["queryStringParameters"][TRACK_ID_PARAM]
    logger.info(f"track_id: {track_id}")

    try:
        response = table.get_item(Key={DYNAMO_PK: track_id})
        item = response['Item']
        logger.info(f"Got item with {DYNAMO_PK}=={track_id}, returning 200.")
        return response_200(event, track_id, item)

    except KeyError:
        logger.info(f"TrackId=={track_id} not in database, returning 404.")
        return response_404(event, track_id)
