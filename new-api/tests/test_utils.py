import unittest
from app import track_id_specified
from app import TRACK_ID_PARAM


class GetHandlerUnitTests(unittest.TestCase):

    def test_track_id_specified_false_when_params_is_none(self):
        self.assertFalse(track_id_specified(None))

    def test_track_id_specified_false_when_track_id_param_is_none(self):
        self.assertFalse(track_id_specified({TRACK_ID_PARAM: None}))

    def test_track_id_specified_true_when_track_id_specified(self):
        self.assertTrue(track_id_specified({TRACK_ID_PARAM: ""}))
