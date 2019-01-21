import unittest
from core.spotify_artist import SpotifyArtist


class TestSpotifyArtist(unittest.TestCase):

    def test_json_constructor(self):
        d = {'name': 'dummy_artist', 'other_attr': 'dummy'}
        artist = SpotifyArtist.from_json(d)
        self.assertEqual(d['name'], artist.name)

