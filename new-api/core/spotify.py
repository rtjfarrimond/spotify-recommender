from core.settings import client_id
from core.settings import client_secret
import spotipy
import spotipy.oauth2 as oauth2


class SpotifyDelegate(object):

    def __init__(self):
        credentials = oauth2.SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret)
        token = credentials.get_access_token()
        if token:
            self.__sp = spotipy.Spotify(auth=token)

    def track(self, track_id):
        return self.__sp.track(track_id)

    def search(self, q, by, limit=10, offset=0):
        return self.__sp.search(q=q, type=by, limit=limit, offset=offset)

