from sounds_like import get
from sounds_like import response_200
from sounds_like import response_400
from sounds_like import response_404
from sounds_like import table_name
from sounds_like import TRACK_ID_PARAM
import boto3
import json
import random
import string
import unittest
import warnings


DYNAMO_TRACK_ID = "TrackId"


def get_random_id():
    ''' Generate random id with  extremely low liklihood of existing in db.

    Generates an id composed of uppercase letters, lowercase letters, and
    numbers. Each id is 16 characters long, so this gives 62C16 possible
    unique combinations (that is, 4.7672401706e+28).
    '''
    return ''.join(random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase,
        k=16))


class GetHandlerIntegrationTest(unittest.TestCase):

    def setUp(self):
        # Ignoring ssl unclosed warning after looking on boto3 gh issues.
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        self.table = self.dynamodb.Table(table_name)
        self.track_id = get_random_id()
        self.table.put_item(Item={DYNAMO_TRACK_ID: self.track_id})

    def tearDown(self):
        self.table.delete_item(Key={DYNAMO_TRACK_ID: self.track_id})

    def test_get_returns_code_400_when_no_params(self):
        dummy_event = {"queryStringParameters": None}
        expected = response_400(dummy_event)
        actual = get(dummy_event, '')
        self.assertEqual(expected, actual)

    def test_get_returns_code_400_when_no_track_id_param(self):
        dummy_event = {"queryStringParameters": {"otherParam": "dummy"}}
        expected = response_400(dummy_event)
        actual = get(dummy_event, '')
        self.assertEqual(expected, actual)

    def test_get_returns_code_404_when_track_id_not_in_db(self):
        random_id = get_random_id()
        dummy_event = {
            "queryStringParameters": {TRACK_ID_PARAM: random_id}
        }
        expected = response_404(dummy_event, random_id)
        actual = get(dummy_event, '')
        self.assertEqual(expected, actual)

    def test_get_returns_code_200_when_track_exists_in_db(self):
        dummy_event = {
            "queryStringParameters": {TRACK_ID_PARAM: self.track_id}
        }
        expected_item = {DYNAMO_TRACK_ID: self.track_id}
        expected = response_200(dummy_event, self.track_id, expected_item)
        actual = get(dummy_event, '')
        self.assertEqual(expected, actual)
