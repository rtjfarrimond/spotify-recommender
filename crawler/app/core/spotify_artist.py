import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpotifyArtist(object):

    name = None

    def __init__(self, d):
        [setattr(self, a, d[a]) for a in d]

    @classmethod
    def from_json(cls, json):
        d = {}
        try:
            d['name'] = json['name']
        except KeyError:
            logger.info(
                'Artist name not found in json, setting to empty string.')
            d['name'] = ''
        return cls(d)

    def __repr__(self):
        if not self.name:
            return ''

        return self.name
