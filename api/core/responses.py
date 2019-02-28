# TODO: Move this into the core package.
import json


def response_200_get_success(event, track_id, item):
    body = {
        "message": f"Fetched item with id {track_id}.",
        "item": item,
        "input": event
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def response_200_put_exists(event, track_id, item):
    body = {
        "message": f"Item with id {track_id} already exists.",
        "item": item,
        "input": event
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }

def response_202(event, track_id):
    body = {
        "message": f"Track preview at {track_id} downloaded from Spotify.",
        "input": event
    }

    return {
        "statusCode": 202,
        "body": json.dumps(body)
    }

def response_204(event, track_id):
    body = {
        "message": f"Track {track_id} has no preview available.",
        "input": event
    }

    return {
        "statusCode": 204,
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

def response_500(event):
    body = {
        "message": f"Internal server error.",
        "input": event
    }

    return {
        "statusCode": 500,
        "body": json.dumps(body)
    }
