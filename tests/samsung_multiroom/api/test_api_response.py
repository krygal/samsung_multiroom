import unittest

from samsung_multiroom.api import ApiResponse


class TestApiResponse(unittest.TestCase):

    def test_parse_successful_response(self):
        response_text = """<?xml version="1.0" encoding="UTF-8"?>
            <UIC>
                <method>VolumeLevel</method>
                <version>1.0</version>
                <speakerip>192.168.1.129</speakerip>
                <user_identifier></user_identifier>
                <response result="ok">
                    <volume>10</volume>
                </response>
            </UIC>"""

        response = ApiResponse(response_text)

        self.assertTrue(response.success)
        self.assertEqual(response.raw, response_text)
        self.assertEqual(response.name, 'VolumeLevel')
        self.assertEqual(response.data, {
            'volume': '10'
        })

    def test_parse_fails_nonxml(self):
        response_text = """Hello there"""

        response = ApiResponse(response_text)

        self.assertFalse(response.success)
        self.assertEqual(response.raw, response_text)
        self.assertEqual(response.name, None)
        self.assertEqual(response.data, None)

    def test_parse_fails_response_notok(self):
        response_text = """<?xml version="1.0" encoding="UTF-8"?>
            <UIC>
                <method>VolumeLevel</method>
                <version>1.0</version>
                <speakerip>192.168.1.129</speakerip>
                <user_identifier></user_identifier>
                <response result="ng"></response>
            </UIC>"""

        response = ApiResponse(response_text)

        self.assertFalse(response.success)
        self.assertEqual(response.raw, response_text)
        self.assertEqual(response.name, 'VolumeLevel')
        self.assertEqual(response.data, {})

    def test_parse_fails_wrong_xml(self):
        response_text = """<?xml version="1.0" encoding="UTF-8"?>
            <UIC>
                <hello>There</hello>
                <response result="ok"></response>
            </UIC>"""

        response = ApiResponse(response_text)

        self.assertFalse(response.success)
        self.assertEqual(response.raw, response_text)
        self.assertEqual(response.name, None)
        self.assertEqual(response.data, None)
