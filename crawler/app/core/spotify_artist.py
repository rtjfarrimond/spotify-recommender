import json


class SpotifyArtist(object):

    def __init__(self, d):
        [setattr(self, a, d[a]) for a in d]

    @classmethod
    def from_json(cls, json):
        d = {}
        d['name'] = json['name']
        return cls(d)

    def __repr__(self):
        if not self.name:
            return ''

        return self.name
