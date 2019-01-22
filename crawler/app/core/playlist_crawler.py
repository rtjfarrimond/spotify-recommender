import spotipy
import spotipy.util
import json
from core.spotify_track import SpotifyTrack


class PlaylistCrawler(object):

    __sp = None
    _json = None
    tracks = None

    def __init__(self, username, playlist_url, audio_path='./audio'):
        if not username:
            raise ValueError('Spotify username not set.')
        if not playlist_url:
            raise ValueError('Spotify playlist URL not set.')
        self.__username = username
        self.__playlist_url = playlist_url
        if audio_path[-1] == '/':
            self.audio_path = audio_path[:-1]
        else:
            self.audio_path = audio_path

    def auth_spotify(self):
        token = spotipy.util.prompt_for_user_token(self.__username)
        if token:
            self.__sp = spotipy.Spotify(auth=token)

    def load_json(self):
        ''' Load the json representation of the playlist at `__playlist_url`.
        '''
        if not self.__sp:
            self.auth_spotify()
        self._json = self.__sp.user_playlist_tracks(
            'spotify',
            playlist_id=self.__playlist_url)

    def parse_json(self):
        ''' Parse fields for each track in the playlist.

        This method parses the json representation of the playlist and creates
        an array of `SpotifyTrack` objects as an instance variable.

        '''
        if not self._json:
            self.load_json()

        if not self.tracks:
            self.tracks = []

        for item in self._json['items']:
            track = item['track']
            if track['preview_url']:
                self.tracks.append(SpotifyTrack.from_json(track))

    def download_previews(self):
        if not self.audio_path:
            raise ValueError('No path to write audio is defined.')
        if not self.tracks:
            self.parse_json()

        for track in self.tracks:
            track.download_preview(self.audio_path)

    def __repr__(self):
        return json.dumps(self.__dict__)

