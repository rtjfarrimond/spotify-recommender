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

    username_dummy = None
    playlist_url_dummy = None
    dl_bucket_name_dummy = None
    crawler = None

    @classmethod
    def setUpClass(cls):
        cls.username_dummy = "userDummy"
        cls.playlist_url_dummy = "urlDummy"
        cls.dl_bucket_name_dummy = "pathDummy"
        cls.crawler = PlaylistCrawler(
            cls.username_dummy,
            cls.playlist_url_dummy)

    def test_default_constructor_happy_path(self):
        self.assertEqual(self.username_dummy, self.crawler.username)
        self.assertEqual(self.playlist_url_dummy, self.crawler.playlist_url)

    def test_default_constructor_happy_path_default_dl_bucket_name(self):
        crawler = PlaylistCrawler(
            self.username_dummy,
            self.playlist_url_dummy)
        self.assertEqual(self.username_dummy, crawler.username)
        self.assertEqual(self.playlist_url_dummy, crawler.playlist_url)

    def test_default_constructor_value_error_when_username_null(self):
        self.assertRaises(
            ValueError,
            PlaylistCrawler,
            None,
            self.playlist_url_dummy)

    def test_default_constructor_value_error_when_playlist_url_null(self):
        self.assertRaises(
            ValueError,
            PlaylistCrawler,
            self.username_dummy,
            None)

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
