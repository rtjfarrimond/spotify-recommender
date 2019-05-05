from core.settings import client_id
from core.settings import client_secret
from core.spotify import SpotifyDelegate
from spotipy.client import SpotifyException
from zipfile import ZipFile
import boto3
import json
import logging
import sys
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
        if not self.track:
            try:
                logger.info(f"Getting track {self.track_id} from Spotify...")
                self.track = self.__sp.track(self.track_id)
                return True
            except SpotifyException as e:
                logger.warning(e)
                return False
        else:
            return True

    def write_track_json(self, file_path):
        if not self.load_track():
            return False
        artists = ', '.join(a['name'] for a in self.track['artists'])
        with open(file_path, 'w') as f:
            track_dict = {
                "track": {
                    "id": self.track_id,
                    "title": self.track['name'],
                    "artists": artists,
                    "preview_url": self.track['preview_url'],
                }
            }
            f.write(json.dumps(track_dict))
        return True

    def download_track(self):
        ''' Downloads target from Spotify and uploads to s3.
        '''
        if not self.load_track():
            return False

        preview_url = self.track['preview_url']
        if not preview_url:
            logger.info(f"No preview available for {self.track_id}")
            return False

        audio_path = f"{DL_PATH}/{self.track_id}.mp3"
        logger.info(f"Downloading preview to {audio_path}...")
        urllib.request.urlretrieve(preview_url, audio_path)

        json_path = f"{DL_PATH}/{self.track_id}.json"
        logger.info(f"Writing metadata to {json_path}...")
        if not self.write_track_json(json_path):
            logger.critical(
                f"Could not write metadata to {json_path}, exiting.")
            sys.exit(1)

        logger.info("Zipping preview and metadata for upload...")
        zip_file_name = f"{DL_PATH}/{self.track_id}.zip"
        with ZipFile(zip_file_name, 'w') as zf:
            zf.write(audio_path)
            zf.write(json_path)

        logger.info(f"Uploading zip to s3 {self.bucket_name}...")
        s3 = boto3.resource('s3')
        with open(zip_file_name, 'rb') as f:
            s3.Bucket(self.bucket_name).put_object(
                Key=f"{self.track_id}.zip", Body=f)

        logger.info(f"Track {self.track_id} uploaded to s3 bucket.")

        return True
