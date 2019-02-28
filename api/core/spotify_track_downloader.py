from core.settings import client_id
from core.settings import client_secret
from core.spotify import SpotifyDelegate
from spotipy.client import SpotifyException
from zipfile import ZipFile
import boto3
import logging
import urllib.request


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DL_PATH = '/tmp'


class SpotifyTrackDownloader(object):

    __sp = None
    track = None

    def __init__(self, bucket_name, track_id):
        self.bucket_name = bucket_name
        self.track_id = track_id
        self.__sp = SpotifyDelegate()

    def load_track(self):
        try:
            logger.info(f"Getting track {self.track_id} from Spotify...")
            self.track = self.__sp.track(self.track_id)
            return True
        except SpotifyException as e:
            logger.warning(e)
            return False

    def get_track_filename(self):
        if not self.track:
            if not self.load_track():
                return False
        artists = ', '.join(a['name'] for a in self.track['artists'])
        title = self.track['name']
        # Replace slashes in filename with colon so as not to break path.
        return f"{artists} - {title}.mp3".replace('/', ':')

    def download_track(self):
        ''' Downloads target from Spotify and uploads to s3.
        '''
        if not self.track:
            if not self.load_track():
                return False
        preview_url = self.track['preview_url']
        if not preview_url:
            logger.info(f"No preview available for {self.track_id}")
            return False

        filename = self.get_track_filename()

        # Happens if spotify client cannot load track
        if filename == False:
            logger.info("Filename not created.")
            return False

        audio_path = f"{DL_PATH}/{filename}"
        logger.info(f"Downloading preview to {audio_path}...")
        urllib.request.urlretrieve(preview_url, audio_path)

        logger.info("Zipping preview for upload...")
        zip_file_name = f"{DL_PATH}/{self.track_id}.zip"
        with ZipFile(zip_file_name, 'w') as zf:
            zf.write(audio_path)

        logger.info(f"Uploading preview to s3 {self.bucket_name}...")
        s3 = boto3.resource('s3')
        with open(zip_file_name, 'rb') as f:
            s3.Bucket(self.bucket_name).put_object(
                Key=f"{self.track_id}.zip", Body=f)

        logger.info(f"Track {self.track_id} uploaded to s3 bucket.")

        return True
