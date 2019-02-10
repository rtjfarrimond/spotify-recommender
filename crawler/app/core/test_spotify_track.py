import unittest
import logging
from core.spotify_track import SpotifyTrack
from core.spotify_artist import SpotifyArtist


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def make_track(
        spotify_id='dummy',
        name='dummy',
        artists=[],
        preview_url='dummy',
        dl_bucket_name='dummy'):
    return SpotifyTrack.from_json({
        'id': spotify_id,
        'name': name,
        'artists': artists,
        'preview_url': preview_url,
        'dl_bucket_name': dl_bucket_name
        })


def artist_strings(list_artists):
    return [str(a) for a in list_artists]


class TestSpotifyTrack(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.spotify_id = "dummy_id"
        cls.name = "track title"
        cls.artist_1 = {"name": "artist_1"}
        cls.artist_2 = {"name": "artist_2"}
        cls.artists = [cls.artist_1, cls.artist_2]
        cls.preview_url = "dummy_url"
        cls.dl_bucket_name = ''

    def test_default_constructor(self):
        attrs = [('attr_1', 'a'), ('attr_2', 'b')]
        d = {k: v for k, v in attrs}
        track = SpotifyTrack(d)
        self.assertTrue(hasattr(track, attrs[0][0]))
        self.assertTrue(track.attr_1, attrs[0][1])
        self.assertTrue(hasattr(track, attrs[1][0]))
        self.assertTrue(track.attr_2, attrs[1][1])
        self.assertIsNone(track.spotify_id)
        self.assertIsNone(track.name)
        self.assertIsNone(track.artists)
        self.assertIsNone(track.preview_url)

    def test_from_json_contructor(self):
        spotify_artists = [SpotifyArtist(name) for name in self.artists]
        track = make_track(
            spotify_id=self.spotify_id,
            name=self.name,
            artists=self.artists,
            preview_url=self.preview_url)
        self.assertEqual(self.spotify_id, track.spotify_id)
        self.assertEqual(self.name, track.name)
        self.assertEqual(
                artist_strings(spotify_artists),
                artist_strings(track.artists))
        self.assertEqual(self.preview_url, track.preview_url)

    def test_download_preview_value_error_when_no_preview_url(self):
        track = SpotifyTrack({})
        self.assertRaises(ValueError, track.download_preview)

    def test_get_artists_string_returns_empty_string_if_no_artists(self):
        track = SpotifyTrack({})
        self.assertEqual('', track.get_artists_string())

    def test_get_artists_string_formatting(self):
        expected = f"{self.artist_1['name']}, {self.artist_2['name']}"
        track = make_track(artists=[self.artist_1, self.artist_2])
        self.assertEqual(expected, track.get_artists_string())

    def test_repr_formatting(self):
        expected = f"{self.artist_1['name']}, " + \
                   f"{self.artist_2['name']} - {self.name}"
        track = make_track(
            name=self.name, artists=[self.artist_1, self.artist_2])
        self.assertEqual(expected, track.__repr__())


if __name__ == '__main__':
    unittest.main()
