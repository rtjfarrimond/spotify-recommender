import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def return_400():
    return {
        "statusCode": 400,
        "body": "trackId parameter not passed."
    }

def get_request_handler(event, context):
    if event["queryStringParameters"] is None:
        return return_400()

    try:
        track_id = event["queryStringParameters"]["trackId"]
        return {
            "statusCode": 200,
            "body": track_id
        }
    except KeyError:
        return return_400()
