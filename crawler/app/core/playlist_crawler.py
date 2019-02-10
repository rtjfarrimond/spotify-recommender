import json
import logging
import spotipy
import spotipy.util
from core.spotify_track import SpotifyTrack


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaylistCrawler(object):

    __sp = None
    first_page = None
    tracks = None

    def __init__(self, username, playlist_url):
        if not username:
            raise ValueError('Spotify username not set.')
        if not playlist_url:
            raise ValueError('Spotify playlist URL not set.')
        self.username = username
        self.playlist_url = playlist_url

    def auth_spotify(self):
        token = spotipy.util.prompt_for_user_token(self.username)
        if token:
            self.__sp = spotipy.Spotify(auth=token)

    def load_first_page(self):
        ''' Load json of first page of playlist at `playlist_url`.
        '''
        if not self.__sp:
            self.auth_spotify()
        self.first_page = self.__sp.user_playlist_tracks(
            'spotify',
            playlist_id=self.playlist_url)

    def get_next_page(self, current):
        return self.__sp.next(current)

    def parse_json(self):
        ''' Parse fields for each track in the playlist.

        This method parses the json representation of the playlist and creates
        an array of `SpotifyTrack` objects as an instance variable.

        '''
        def parse_page(page, page_number):
            logger.info(f'Parsing playlist page {page_number}...')
            for item in page['items']:
                track = item['track']
                if track['preview_url']:
                    self.tracks.append(
                        SpotifyTrack.from_json(track))

        logger.info("Parsing preview URLs from playlist...")

        if not self.tracks:
            self.tracks = []

        if not self.first_page:
            self.load_first_page()

        counter = 1
        parse_page(self.first_page, counter)

        current_page = self.first_page
        while current_page['next']:
            counter += 1
            current_page = self.get_next_page(current_page)
            parse_page(current_page, counter)

    def download_previews(self):
        if not self.tracks:
            self.parse_json()

        logger.info("Downloading track previews...")
        for track in self.tracks:
            track.download_preview()

    def __repr__(self):
        return json.dumps(self.__dict__)

