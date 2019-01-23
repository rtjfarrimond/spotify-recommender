import unittest
from core.spotify_artist import SpotifyArtist


class TestSpotifyArtist(unittest.TestCase):

    def test_default_constructor(self):
        attrs = [('attr_1', 'a'), ('attr_2', 'b')]
        d = {k: v for k, v in attrs}
        artist = SpotifyArtist(d)
        self.assertTrue(hasattr(artist, attrs[0][0]))
        self.assertTrue(artist.attr_1, attrs[0][1])
        self.assertTrue(hasattr(artist, attrs[1][0]))
        self.assertTrue(artist.attr_2, attrs[1][1])

    def test_json_constructor_with_populated_name(self):
        dummy_attr = 'other_attr'
        d = {'name': 'dummy_artist', dummy_attr: 'dummy'}
        artist = SpotifyArtist.from_json(d)
        self.assertEqual(d['name'], artist.name)
        self.assertFalse(hasattr(artist, dummy_attr))

    def test_json_constructor_unpopulated_name_set_name_empty_string(self):
        dummy_attr = 'other_attr'
        d = {dummy_attr: 'dummy'}
        artist = SpotifyArtist.from_json(d)
        self.assertEqual('', artist.name)
        self.assertFalse(hasattr(artist, dummy_attr))

    def test_repr_empty_string_when_name_not_set(self):
        artist = SpotifyArtist({})
        self.assertEqual(str(artist), '')

    def test_repr_is_name_when_name_is_set(self):
        expected = 'Threepac Shakhurr'
        artist = SpotifyArtist.from_json({'name': expected})
        self.assertEqual(str(artist), expected)
