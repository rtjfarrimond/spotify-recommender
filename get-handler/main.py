import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_handler(event, context):
    return {
        "statusCode": 200,
        "body": "Heller der wrld."
    }
