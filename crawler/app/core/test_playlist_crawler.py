import unittest
from core.spotify_track import SpotifyTrack
from core.playlist_crawler import PlaylistCrawler


class MockSpotifyTrack(SpotifyTrack):

    def __init__(self):
        pass


class TestPlaylistCrawler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_default_constructor_happy_path(self):
        self.assertTrue(False)

    def test_default_constructor_value_error_when_username_null(self):
        self.assertRaises(ValueError, PlaylistCrawler, None, "dummyPlaylist")

    def test_default_constructor_value_error_when_playlist_url_null(self):
        self.assertTrue(False)

    def test_default_constructor_trims_trailing_slash_from_playlist_url(self):
        self.assertTrue(False)

    def test_parse_json_single_page(self):
        self.assertTrue(False)

    def test_parse_json_multiple_pages(self):
        self.assertTrue(False)

    def test_download_previews(self):
        # Mock SpotifyTrack for this
        self.assertTrue(False)

    def test_repr(self):
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
