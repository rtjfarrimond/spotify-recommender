import unittest
from main import get_request_handler as handler
from main import return_400


class GetHandlerUnitTests(unittest.TestCase):

    def test_request_handler_code_400_when_malformed(self):
        expected_response = return_400()
        event = {"queryStringParameters": {"unexpected_param": "dummy"}}
        actual_response = handler(event, None)

        self.assertEqual(expected_response, actual_response)
