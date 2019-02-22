from botocore.exceptions import ClientError
from responses import *
import boto3
import json
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TRACK_ID_PARAM = "trackId"
DYNAMO_PK = "TrackId" # TODO: put this in ssm

# TODO: Put table_name in SSM with serverless then fetch from there.
table_name = os.getenv("TRACKS_TABLE", "spot-rec-api-dev-dynamodb")
region = os.getenv("REGION", "eu-west-1")
logger.info(f"table_name: {table_name}")
logger.info(f"region: {region}")

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

def put(event, context):
    if not track_id_specified(event["queryStringParameters"]):
        return response_400(event)

    track_id = event["queryStringParameters"][TRACK_ID_PARAM]
    logger.info(f"track_id: {track_id}")
    body = {
        "message": f"PUT function executed with TrackId: {track_id}!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

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


if __name__ == '__main__':
    print(get({"queryStringParameters": None}, ''))
    print(get({"queryStringParameters": {TRACK_ID_PARAM: "dummyTrack"}}, ''))
