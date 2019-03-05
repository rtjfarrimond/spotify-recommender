from core.spotify_track import SpotifyTrack
import json
import logging
import spotipy
import spotipy.oauth2 as oauth2
import spotipy.util


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaylistCrawler(object):

    __sp = None
    first_page = None
    tracks = None

    def __init__(self, playlist_url, client_id, client_secret):
        if not playlist_url:
            raise ValueError('Spotify playlist URL not set.')

        self.playlist_url = playlist_url
        self.client_id = client_id
        self.client_secret = client_secret

    def auth_spotify(self):
        credentials = oauth2.SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret)

        token = credentials.get_access_token()
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

    def write_tracks_to_json(self, json_file_name):
        with open(json_file_name, 'w') as f:
            for track in self.tracks:
                track_dict = {
                    "track": {
                        "id": track.spotify_id,
                        "title": track.name,
                        "artists": track.get_artists_string(),
                        "preview_url": track.preview_url
                    }
                }
                f.write(f"{json.dumps(track_dict)},\n")

    def __repr__(self):
        return json.dumps(self.__dict__)
