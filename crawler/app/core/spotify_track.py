import os
import urllib.request
from core.spotify_artist import SpotifyArtist


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

    def download_preview(self, path):
        ''' Download the 30s preview of the track from Spotify Web API.

        Parameters:
        -----------
        path:
            string, the path the preview should be saved to.
        '''
        if not self.preview_url:
            raise ValueError('Track does not define a preview_url.')
        print(f'Downloading preview for: {self}')
        urllib.request.urlretrieve(self.preview_url, f'{path}/{self}.mp3')

    def get_artists_string(self):
        if not self.artists:
            return ''
        return ', '.join([str(a) for a in self.artists])

    def __repr__(self):
        return f"{self.get_artists_string()} - {self.name}"
