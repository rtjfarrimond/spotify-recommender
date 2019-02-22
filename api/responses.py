import json


def response_200(event, track_id, item):
    body = {
        "message": f"Fetched item with id {track_id}.",
        "item": item,
        "input": event
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def response_400(event):
    body = {
        "message": "trackId parameter not passed.",
        "input": event
    }

    return {
        "statusCode": 400,
        "body": json.dumps(body)
    }

def response_404(event, track_id):
    body = {
        "message": f"Resource with trackId {track_id} not found.",
        "input": event
    }

    return {
        "statusCode": 404,
        "body": json.dumps(body)
    }
