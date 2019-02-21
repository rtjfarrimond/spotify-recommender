import boto3
import json
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TRACK_ID_PARAM = "trackId"

table_name = os.getenv("TRACKS_TABLE", "")
logger.info(f"table_name: {table_name}")

# TODO: Get region from the environment.
dynamodb = boto3.resource("dynamodb", region_name="eu-west-1")

response_400 = {
    "statusCode": 400,
    "body": "trackId parameter not passed."
}

def put(event, context):
    body = {
        "message": "PUT function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

def get(event, context):
    if event["queryStringParameters"] == None:
        return response_400

    try:
        track_id = event["queryStringParameters"][TRACK_ID_PARAM]
        logger.info(f"track_id: {track_id}")
        body = {
            "message": f"GET function executed with trackId: {track_id}!",
            "input": event
        }

        return {
            "statusCode": 200,
            "body": json.dumps(body)
        }

    except (KeyError, TypeError):
        return response_400


if __name__ == '__main__':
    print(get({"queryStringParameters": None}, ''))
    print(get({"queryStringParameters": {TRACK_ID_PARAM: "dummyTrack"}}, ''))
