from core.spotify import SpotifyDelegate
from core.spotify_track_downloader import SpotifyTrackDownloader
import unittest


class MockSpotifyTrackDownloader(SpotifyTrackDownloader):

    def __init__(self, track):
        self.track = track


class SpotifyTrackDownloaderUnitTests(unittest.TestCase):

    def setUp(self):
        self.bucket_name = "dummyBucketName"
        self.track_id = "dummyTrackId"
        self.downloader = SpotifyTrackDownloader(
            self.bucket_name, self.track_id)

    def test_load_track_returns_false_for_dummy_id(self):
        self.assertFalse(self.downloader.load_track())
        self.assertIsNone(self.downloader.track)

    def test_get_track_filename_false_for_dummy_id(self):
        self.assertFalse(self.downloader.get_track_filename())

    def test_download_track_false_for_dummy_id(self):
        self.assertFalse(self.downloader.download_track())

    def test_get_track_filename(self):
        input_artist_1_name = "dummyArtist1"
        input_artist_2_name = "dummyArtist2"
        input_track_name = "dummy/TrackName"
        expected_track_name = "dummy:TrackName"
        expected_filename = f"{input_artist_1_name}, " + \
                            f"{input_artist_2_name} - " + \
                            f"{expected_track_name}.mp3"

        track = {
            "artists": [
                {"name": input_artist_1_name},
                {"name": input_artist_2_name}
            ],
            "name": expected_track_name
        }

        downloader = MockSpotifyTrackDownloader(track)
        self.assertEqual(expected_filename, downloader.get_track_filename())
