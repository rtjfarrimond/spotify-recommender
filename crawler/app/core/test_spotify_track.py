import unittest
import logging
from core.spotify_track import SpotifyTrack
from core.spotify_artist import SpotifyArtist


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def make_track(
        spotify_id='dummy',
        name='dummy',
        artists='dummy',
        preview_url='dummy'):
    return SpotifyTrack({
        'id': spotify_id,
        'name': name,
        'artists': artists,
        'preview_url': preview_url
        })


class TestSpotifyTrack(unittest.TestCase):

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
        def artist_strings(list_artists):
            return [str(a) for a in list_artists]

        artists = [{'name': 'artist_1'}, {'name': 'artist_2'}]
        spotify_artists = [SpotifyArtist(name) for name in artists]
        d = {'id': 'dummy_id',
             'name': 'dummy_name',
             'artists': artists,
             'preview_url': 'dummy_url'}
        track = SpotifyTrack.from_json(d)
        self.assertEqual(d['id'], track.spotify_id)
        self.assertEqual(d['name'], track.name)
        self.assertEqual(
                artist_strings(spotify_artists),
                artist_strings(track.artists))
        self.assertEqual(d['preview_url'], track.preview_url)

    def test_download_preview_value_error_when_no_preview_url(self):
        track = SpotifyTrack({})
        self.assertRaises(ValueError, track.download_preview, 'path')

    def test_get_artists_string_returns_empty_string_if_no_artists(self):
        track = SpotifyTrack({})
        self.assertEqual('', track.get_artists_string())

    def test_get_artists_string_formatting(self):
        artist_1 = 'artist_1'
        artist_2 = 'artist_2'
        expected = f'{artist_1}, {artist_2}'
        track = SpotifyTrack.from_json(
                {'id': 'dummy',
                 'name': 'dummy',
                 'artists': [{'name': artist_1}, {'name': artist_2}],
                 'preview_url': 'dummy'})
        self.assertEqual(expected, track.get_artists_string())

    def test_repr_formatting(self):
        artist_1 = 'artist_1'
        artist_2 = 'artist_2'
        name = 'track title'
        expected = f'{artist_1}, {artist_2} - {name}'
        track = SpotifyTrack.from_json(
                {'id': 'dummy',
                 'name': name,
                 'artists': [{'name': artist_1}, {'name': artist_2}],
                 'preview_url': 'dummy'})
        self.assertEqual(expected, track.__repr__())

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
