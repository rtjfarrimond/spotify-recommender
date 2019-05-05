from core.spotify_artist import SpotifyArtist
import logging
import urllib.request


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpotifyTrack(object):

    spotify_id = None
    name = None
    artists = None
    preview_url = None

    def __init__(self, d):
        [setattr(self, a, d[a]) for a in d.keys()]

    @classmethod
    def from_json(cls, track):
        d = {}
        d['spotify_id'] = track['id']
        d['name'] = track['name']
        d['artists'] = [SpotifyArtist.from_json(a) for a in track['artists']]
        d['preview_url'] = track['preview_url']
        return cls(d)

    def download_preview(self):
        ''' Download the 30s preview of the track from Spotify Web API.
        '''
        if not self.preview_url:
            raise ValueError('Track does not define a preview_url.')

        try:
            logger.info(f'Downloading preview for: {self}')
            filename = f"{self.spotify_id}.mp3"
            audio_path = f'/tmp/{filename}'
            urllib.request.urlretrieve(
                self.preview_url,
                audio_path)
        except urllib.error.URLError as urle:
            logger.warn(f"URLError when downloading:\n {urle}")

    def get_artists_string(self):
        if not self.artists:
            return ''
        return ', '.join([str(a) for a in self.artists])

    def __repr__(self):
        return f"{self.get_artists_string()} - {self.name}"
