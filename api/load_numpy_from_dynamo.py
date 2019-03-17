# This script illustrates how to load features from DynamoDB
from core.settings import DYNAMODB_TABLE
import boto3
import pickle


dynamodb = boto3.resource('dynamodb', region_name="eu-west-1")
table = dynamodb.Table(DYNAMODB_TABLE)
response = table.scan()

for item in response['Items']:
    try:
        f = item['Features']
        print(type(f))
        p = pickle.loads(bytes(f, encoding="ASCII"), encoding="latin1")
        print(p)
        print(type(p))
    except KeyError:
        pass
