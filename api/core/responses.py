import json


def make_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body)
    }


def response_200_get_success(event, track_id, results):
    body = {
        "message": f"Fetched sounds like results for query track: {track_id}.",
        "input": event,
        "results": results
    }

    return make_response(200, body)


def response_200_put_exists(event, track_id, item):
    body = {
        "message": f"Item with id {track_id} already exists.",
        "input": event
    }

    return make_response(200, body)

def response_202(event, track_id):
    body = {
        "message": f"Track preview at {track_id} downloaded from Spotify.",
        "input": event
    }

    return make_response(202, body)


def response_204(event, track_id):
    body = {
        "message": f"Track {track_id} has no preview available.",
        "input": event
    }

    return make_response(204, body)


def response_400(event):
    body = {
        "message": "trackId parameter not passed.",
        "input": event
    }

    return make_response(400, body)


def response_404(event, track_id):
    body = {
        "message": f"Resource with trackId {track_id} not found.",
        "input": event
    }

    return make_response(404, body)


def response_500(event):
    body = {
        "message": f"Internal server error.",
        "input": event
    }

    return make_response(500, body)
