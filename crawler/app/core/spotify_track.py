import boto3
import urllib.request
import logging
from core.spotify_artist import SpotifyArtist
from util.string_utils import escape_forwardslash


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpotifyTrack(object):

    spotify_id = None
    name = None
    artists = None
    preview_url = None
    dl_bucket_name = None

    def __init__(self, d, dl_bucket_name=None):
        if not dl_bucket_name:
            raise ValueError("S3 bucket name not set.")
        self.dl_bucket_name = dl_bucket_name
        logger.info(f"Spotify track: {self.dl_bucket_name}")
        [setattr(self, a, d[a]) for a in d.keys()]

    @classmethod
    def from_json(cls, track, dl_bucket_name=None):
        if not dl_bucket_name:
            raise ValueError("S3 bucket name not set.")
        logger.info(f"Spotify track json: {cls.dl_bucket_name}")

        d = {}
        d['spotify_id'] = track['id']
        d['name'] = track['name']
        d['artists'] = [SpotifyArtist.from_json(a) for a in track['artists']]
        d['preview_url'] = track['preview_url']
        return cls(d, dl_bucket_name)

    def download_preview(self, path):
        ''' Download the 30s preview of the track from Spotify Web API.

        Parameters:
        -----------
        path:
            string, the path the preview should be saved to.
        '''
        if not self.preview_url:
            raise ValueError('Track does not define a preview_url.')

        if not self.dl_bucket_name:
            raise ValueError('S3 bucket name not set.')

        logger.info(f'Downloading preview for: {self}')
        filename = f"{escape_forwardslash(str(self))}.mp3"
        audio_path = f'{path}/{filename}'
        urllib.request.urlretrieve(
            self.preview_url,
            audio_path)

        s3 = boto3.resource('s3')
        with open(audio_path, 'rb') as f:
            s3.Bucket(self.dl_bucket_name).put_object(Key=filename, Body=f)

    def get_artists_string(self):
        if not self.artists:
            return ''
        return ', '.join([str(a) for a in self.artists])

    def __repr__(self):
        return f"{self.get_artists_string()} - {self.name}"
