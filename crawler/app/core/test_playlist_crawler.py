import unittest
from core.spotify_track import SpotifyTrack
from core.playlist_crawler import PlaylistCrawler


def get_page():
    track = {
        "preview_url": "dummyUrl",
        "id": "dummyId",
        "name": "dummyName",
        "artists": [{"name": "dummyArtist"}]}
    items = [{"track": track}]
    return {"items": items, "next": None}, track


class MockSpotifyTrack(SpotifyTrack):

    def __init__(self):
        self.downloaded = False

    def download_preview(self):
        self.downloaded = True


class MockPlaylistCrawler(PlaylistCrawler):

    def __init__(self, first_page):
        self.first_page = first_page

    def get_next_page(self, current):
        d, _ = get_page()
        return d


class TestPlaylistCrawler(unittest.TestCase):

    playlist_url_dummy = None
    crawler = None

    @classmethod
    def setUpClass(cls):
        cls.playlist_url_dummy = "urlDummy"
        cls.client_id_dummy = "clientIdDummy"
        cls.client_secret_dummy = "clientSecretDummy"
        cls.crawler = PlaylistCrawler(
            cls.playlist_url_dummy,
            cls.client_id_dummy,
            cls.client_secret_dummy)

    def test_default_constructor_happy_path(self):
        self.assertEqual(self.playlist_url_dummy, self.crawler.playlist_url)
        self.assertEqual(self.client_id_dummy, self.crawler.client_id)
        self.assertEqual(self.client_secret_dummy, self.crawler.client_secret)

    def test_default_constructor_happy_path_default_dl_bucket_name(self):
        crawler = PlaylistCrawler(
            self.playlist_url_dummy,
            self.client_id_dummy,
            self.client_secret_dummy)
        self.assertEqual(self.playlist_url_dummy, crawler.playlist_url)
        self.assertEqual(self.client_id_dummy, crawler.client_id)
        self.assertEqual(self.client_secret_dummy, crawler.client_secret)

    def test_default_constructor_value_error_when_playlist_url_null(self):
        self.assertRaises(
            ValueError,
            PlaylistCrawler,
            None,
            self.client_id_dummy,
            self.client_secret_dummy)

    def test_parse_json_single_page(self):
        d, track = get_page()
        mock_crawler = MockPlaylistCrawler(d)
        mock_crawler.parse_json()

        expected = [SpotifyTrack.from_json(track)]
        actual = mock_crawler.tracks

        self.assertEqual(len(expected), len(actual))
        self.assertEqual(expected[0].__repr__(), actual[0].__repr__())

    def test_parse_json_multiple_pages(self):
        d, track = get_page()
        d["next"] = "dummyNext"
        mock_crawler = MockPlaylistCrawler(d)
        mock_crawler.parse_json()

        expected = [SpotifyTrack.from_json(track)] * 2
        actual = mock_crawler.tracks

        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertEqual(expected[i].__repr__(), actual[i].__repr__())

    def test_download_previews(self):
        mock_track_1 = MockSpotifyTrack()
        mock_track_2 = MockSpotifyTrack()

        self.crawler.tracks = [mock_track_1, mock_track_2]
        for track in self.crawler.tracks:
            self.assertFalse(track.downloaded)

        self.crawler.download_previews()
        for track in self.crawler.tracks:
            self.assertTrue(track.downloaded)


if __name__ == '__main__':
    unittest.main()
