from core.spotify import SpotifyDelegate
from core.spotify_track_downloader import SpotifyTrackDownloader
from pathlib import Path
import json
import os
import unittest


class MockSpotifyTrackDownloader(SpotifyTrackDownloader):

    def __init__(self, track):
        self.track = track
        self.track_id = track["id"]


class SpotifyTrackDownloaderUnitTests(unittest.TestCase):

    def setUp(self):
        self.bucket_name = "dummyBucketName"
        self.track_id = "dummyTrackId"
        self.downloader = SpotifyTrackDownloader(
            self.bucket_name, self.track_id)

    def test_load_track_returns_false_for_dummy_id(self):
        self.assertFalse(self.downloader.load_track())
        self.assertIsNone(self.downloader.track)

    def test_download_track_false_for_dummy_id(self):
        self.assertFalse(self.downloader.download_track())

    def test_write_track_json(self):
        dummy_title = "dummyTitle"
        dummy_artist_name_1 = "dummyName1"
        dummy_artist_name_2 = "dummyName2"
        dummy_artists = [
            {"name": dummy_artist_name_1},
            {"name": dummy_artist_name_2}
        ]
        dummy_preview_url = "dummyPreviewUrl"

        dummy_track = {
            "id": self.track_id,
            "name": dummy_title,
            "artists": dummy_artists,
            "preview_url": dummy_preview_url
        }

        mock_downloader = MockSpotifyTrackDownloader(dummy_track)
        json_path = "/tmp/test_write_track_json.json"

        mock_downloader.write_track_json(json_path)

        expected = {
            "track": {
                "id": self.track_id,
                "title": dummy_title,
                "artists": f"{dummy_artist_name_1}, {dummy_artist_name_2}",
                "preview_url": dummy_preview_url
            }
        }
        actual = json.loads(Path(json_path).read_text())
        os.remove(json_path)

        self.assertEqual(expected, actual)
