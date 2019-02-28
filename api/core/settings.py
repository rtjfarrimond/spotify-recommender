import boto3


def __get_parameter(name):
    if not name or name == "":
        raise ValueError("name not passed.")

    client = boto3.client('ssm')
    response = client.get_parameter(Name=name)
    return response ['Parameter']['Value']

client_id = __get_parameter('/spot-rec/shared/client_id')
client_secret = __get_parameter('/spot-rec/shared/client_secret')
