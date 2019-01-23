import unittest
import logging
from core.spotify_track import SpotifyTrack
from core.spotify_artist import SpotifyArtist


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
        pass

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
