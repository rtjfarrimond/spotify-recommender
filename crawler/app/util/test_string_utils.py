import unittest
from util.string_utils import escape_forwardslash


class TestStringUtils(unittest.TestCase):

    def test_escape_forwardslash(self):
        string = "this/that"
        expected = "this:that"
        actual = escape_forwardslash(string)

        self.assertEqual(expected, actual)
