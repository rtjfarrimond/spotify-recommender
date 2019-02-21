import boto3
import json
import unittest
import warnings
from main import get_table_name
from main import get_request_handler as handler


class GetHandlerIntegrationTest(unittest.TestCase):

    def setUp(self):
        # Ignoring ssl unclosed warning after looking on boto3 gh issues.
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        self.table = self.dynamodb.Table(get_table_name())
        self.track_id = "dummyId"
        self.table.put_item(Item={'TrackId': self.track_id})

    def tearDown(self):
        self.table.delete_item(Key={'TrackId': self.track_id})

    def test_request_handler_code_400_when_not_exist(self):
       response = handler('', '')
