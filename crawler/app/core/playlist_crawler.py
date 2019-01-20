import spotipy
import spotipy.util


class PlaylistCrawler(object):

    __sp = None

    def __init__(self, username, playlist_url):
        if not username:
            raise ValueError('Spotify username not set.')
        if not playlist_url:
            raise ValueError('Spotify playlist URL not set.')
        self.__username = username
        self.__playlist_url = playlist_url

    def auth_spotify(self):
        token = spotipy.util.prompt_for_user_token(self.__username)
        if token:
            self.__sp = spotipy.Spotify(auth=token)

    def get_playlist_json(self):
        if not self.__sp:
            self.auth_spotify()
        return self.__sp.user_playlist_tracks(
            'spotify',
            playlist_id=self.__playlist_url)
