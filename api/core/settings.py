import boto3


def __get_parameter(name):
    if not name or name == "":
        raise ValueError("name not passed.")

    system_code = "spot-rec"
    name = f"/{system_code}/{name}"
    client = boto3.client('ssm')
    response = client.get_parameter(Name=name)
    return response ['Parameter']['Value']


client_id = __get_parameter('shared/client_id')
client_secret = __get_parameter('shared/client_secret')
DYNAMODB_TABLE = __get_parameter('dynamodb')
DYNAMODB_TABLE_HASH_KEY = __get_parameter('dynamodb_hash_key_name')
DYNAMODB_TABLE_SORT_KEY = __get_parameter('dynamodb_sort_key_name')
AUDIO_UPLOAD_BUCKET = __get_parameter('audio_bucket_name')
