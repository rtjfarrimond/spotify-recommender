import unittest
from util.string_utils import escape_forwardslash_in_basename


class TestStringUtils(unittest.TestCase):

    def test_escape_forwardslash_in_basename(self):
        string = "this/that"
        expected = "this:that"
        actual = escape_forwardslash_in_basename(string)

        self.assertEqual(expected, actual)
