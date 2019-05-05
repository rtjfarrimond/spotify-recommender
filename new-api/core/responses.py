import json


def to_json_string(status_code, body):
    return json.dumps({
        "statusCode": status_code,
        "body": body
    })


def response_200_get_success(event, track_id, results):
    body = {
        "message": f"Fetched sounds like results for query track: {track_id}.",
        "input": event,
        "results": results
    }

    return to_json_string(200, body)


def response_200_put_exists(event, track_id, item):
    body = {
        "message": f"Item with id {track_id} already exists.",
        "item": item,
        "input": event
    }

    return to_json_string(200, body)

def response_202(event, track_id):
    body = {
        "message": f"Track preview at {track_id} downloaded from Spotify.",
        "input": event
    }

    return to_json_string(202, body)


def response_204(event, track_id):
    body = {
        "message": f"Track {track_id} has no preview available.",
        "input": event
    }

    return to_json_string(204, body)


def response_400(event):
    body = {
        "message": "trackId parameter not passed.",
        "input": event
    }

    return to_json_string(400, body)


def response_404(event, track_id):
    body = {
        "message": f"Resource with trackId {track_id} not found.",
        "input": event
    }

    return to_json_string(404, body)


def response_500(event):
    body = {
        "message": f"Internal server error.",
        "input": event
    }

    return to_json_string(500, body)
