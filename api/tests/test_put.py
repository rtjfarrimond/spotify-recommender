from app import put
from app import BUCKET_NAME
from app import DYNAMO_HASH
from app import DYNAMO_SORT
from app import TABLE_NAME
from core.responses import *
from core.settings import DYNAMODB_TABLE_HASH_KEY
from core.settings import DYNAMODB_TABLE_SORT_KEY
from core.spotify import SpotifyDelegate
from core.spotify_track_downloader import SpotifyTrackDownloader
import boto3
import logging
import unittest
import warnings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: Source hardcoded to spotify until we support multiple sources properly.
TEST_ID = "test_id"
TEST_SOURCE = "spotify"


def get_known_track_id(with_preview=True):
    ''' Uses Spotify web api search endpoint to get existing track id.
    '''
    sp = SpotifyDelegate()
    offset = 0
    n = 10
    response = sp.search('care', 'track', limit=n)

    while offset <= 100:
        for track in response['tracks']['items']:
            if with_preview and track['preview_url']:
                logger.info(f"Returning {track['id']} with preview url.")
                return track['id']
            elif not with_preview and not track['preview_url']:
                logger.info(f"Returning {track['id']} with no preview url.")
                return track['id']

            # I still haven't found what I'm looking for.
            out = "out" if not with_preview else ""
            logger.info(
                f"Track with{out} preview not found, fetching next {n}...")
            offset += n
            response = sp.search('love', 'track', limit=n, offset=offset)
    return False

class MockSpotifyTrackDownloader(SpotifyTrackDownloader):

    def __init__(self, downloaded):
        self.downloaded = downloaded

    def download_track(self):
        return self.downloaded


class PutHandlerUnitTests(unittest.TestCase):

    def setUp(self):
        self.track_id = "dummyTrackId"
        self.event = {"queryStringParameters": {"trackId": self.track_id}}

    def test_400_response_when_no_track_id_passed(self):
        event = {"queryStringParameters": {}}
        expected = response_400(event)
        actual = put(event, None)
        self.assertEqual(expected, actual)

    def test_response_204_when_downloaded_is_false(self):
        expected = response_204(self.event, self.track_id)
        mock_downloader = MockSpotifyTrackDownloader(False)
        actual = put(self.event, None, downloader=mock_downloader)
        self.assertEqual(expected, actual)

    def test_response_202_when_downloaded_is_true(self):
        expected = response_202(self.event, self.track_id)
        mock_downloader = MockSpotifyTrackDownloader(True)
        actual = put(self.event, None, downloader=mock_downloader)
        self.assertEqual(expected, actual)

    def test_response_500_when_downloaded_not_boolean(self):
        expected = response_500(self.event)
        mock_downloader = MockSpotifyTrackDownloader(None)
        actual = put(self.event, None, downloader=mock_downloader)
        self.assertEqual(expected, actual)


class PutHandlerIntegrationTests(unittest.TestCase):

    def setUp(self):
        # Ignoring ssl unclosed warning after looking on boto3 gh issues.
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        self.table = self.dynamodb.Table(TABLE_NAME)
        self.table.put_item(
            Item={
                DYNAMODB_TABLE_HASH_KEY: TEST_ID,
                DYNAMODB_TABLE_SORT_KEY: TEST_SOURCE
            }
        )

    def tearDown(self):
        self.table.delete_item(
            Key={
                DYNAMODB_TABLE_HASH_KEY: TEST_ID,
                DYNAMODB_TABLE_SORT_KEY: TEST_SOURCE
            }
        )

    def test_response_204_when_no_preview_available_for_track(self):
        track_id = get_known_track_id(False)
        if not track_id:
            self.fail("Could not get a track id without a preview url.")
        dummy_event = {"queryStringParameters": {"trackId": track_id}}
        self.assertEqual(
            response_204(dummy_event, track_id), put(dummy_event, None))

    def test_track_uploaded_to_s3(self):
        track_id = get_known_track_id()
        logger.info(track_id)
        if not track_id:
            self.fail("Could not get a track id with a preview url.")
        expected_zip = f"{track_id}.zip"
        dummy_event = {"queryStringParameters": {"trackId": track_id}}

        # Assert response is 202.
        self.assertEqual(
            response_202(dummy_event, track_id), put(dummy_event, None))

        # Assert actually uploaded.
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(BUCKET_NAME)
        keys = [obj.key for obj in bucket.objects.all()]
        self.assertTrue(expected_zip in keys)

        # Clean up
        bucket.delete_objects(Delete={"Objects": [{"Key": expected_zip}]})

    def test_response_200_put_exists_if_track_exists_in_db(self):
        dummy_event = {"queryStringParameters": {"trackId": TEST_ID}}
        expected_item = {
            DYNAMO_HASH: TEST_ID,
            DYNAMO_SORT: TEST_SOURCE
        }
        expected = response_200_put_exists(dummy_event, TEST_ID, expected_item)
        actual = put(dummy_event, None)

        self.assertEqual(expected, actual)
