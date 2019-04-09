from boto3.dynamodb.types import Binary
from core.responses import *
from core.settings import ANNOY_INDEX_COL
from core.settings import DYNAMODB_TABLE_HASH_KEY
from core.settings import DYNAMODB_TABLE_SORT_KEY
from core.settings import FEATURE_COL
from core.settings import FEATURE_VECTOR_LENGTH
from app import get
from app import TABLE_NAME
from app import TRACK_ID_PARAM
import boto3
import json
import logging
import numpy as np
import pickle
import random
import string
import unittest
import uuid
import warnings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: Hard coded to spotify until we properly support multiple sources.
source = "spotify"


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

    def get_dummy_features(self):
        a = np.random.rand(FEATURE_VECTOR_LENGTH)
        return pickle.dumps(a, protocol=0)

    def setUp(self):
        # Ignoring ssl unclosed warning after looking on boto3 gh issues.
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        self.table = self.dynamodb.Table(TABLE_NAME)
        self.track_id = get_random_id()
        self.dummy_features = self.get_dummy_features()
        self.dummy_item = {
            DYNAMODB_TABLE_HASH_KEY: self.track_id,
            DYNAMODB_TABLE_SORT_KEY: source,
            ANNOY_INDEX_COL: uuid.uuid1().int>>114,
            FEATURE_COL: Binary(self.dummy_features)
        }
        logger.info(f"Adding dummy record for {self.track_id}...")
        self.table.put_item(Item=self.dummy_item)

    def tearDown(self):
        logger.info(f"Removing dummy record for {self.track_id}...")
        self.table.delete_item(
            Key={
                DYNAMODB_TABLE_HASH_KEY: self.track_id,
                DYNAMODB_TABLE_SORT_KEY: source
            }
        )

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
        expected = 200
        response = get(dummy_event, '')
        d_response = json.loads(response)
        actual = d_response["statusCode"]
        self.assertEqual(expected, actual)
