import unittest
from unittest.mock import MagicMock

from samsung_multiroom.api import ApiResponse
from samsung_multiroom.api import ApiStream


class TestApiStream(unittest.TestCase):

    @unittest.mock.patch('socket.socket')
    def test_open_working_stream(self, s):
        s.return_value.recv.side_effect = [
            b"""HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 215
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>RequestDeviceInfo</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier>public</user_identifier><response result="ok"></response></UIC>""",
            b"""HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 678
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>MainInfo</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier></user_identifier><response result="ok"><party>off</party><partymain></partymain><grouptype>N</grouptype><groupmainip>0.0.0.0</groupmainip><groupmainmacaddr>00:00:00:00:00:00</groupmainmacaddr><spkmacaddr>xx:xx:xx:xx:xx:xx</spkmacaddr><spkmodelname>HW-K650</spkmodelname><groupmode>none</groupmode><channeltype>front</channeltype><channelvolume>0</channelvolume><multichinfo>on</multichinfo><groupspknum>1</groupspknum><dfsstatus>dfsoff</dfsstatus><protocolver>2.3</protocolver><btmacaddr>yy:yy:yy:yy:yy:yy</btmacaddr></response></UIC>""",
        ]

        expected_responses = [
            {
                'success': True,
                'name': 'RequestDeviceInfo',
            },
            {
                'success': True,
                'name': 'MainInfo',
            }
        ]

        stream = ApiStream('192.168.1.129')

        responses = list(stream.open('/UIC?cmd=%3Cname%3EGetMainInfo%3C/name%3E'))

        s.return_value.connect.assert_called_once_with(('192.168.1.129', 55001))

        self.assertEqual(len(responses), len(expected_responses))

        for i, response in enumerate(responses):
            self.assertIsInstance(response, ApiResponse)
            self.assertEqual(response.success, expected_responses[i]['success'])
            self.assertEqual(response.name, expected_responses[i]['name'])


    @unittest.mock.patch('socket.socket')
    def test_open_multiple_responses_in_recv(self, s):
        s.return_value.recv.side_effect = [
            b"""HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 215
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>RequestDeviceInfo</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier>public</user_identifier><response result="ok"></response></UIC>""",

            b"""HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 678
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>MainInfo</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier></user_identifier><response result="ok"><party>off</party><partymain></partymain><grouptype>N</grouptype><groupmainip>0.0.0.0</groupmainip><groupmainmacaddr>00:00:00:00:00:00</groupmainmacaddr><spkmacaddr>xx:xx:xx:xx:xx:xx</spkmacaddr><spkmodelname>HW-K650</spkmodelname><groupmode>none</groupmode><channeltype>front</channeltype><channelvolume>0</channelvolume><multichinfo>on</multichinfo><groupspknum>1</groupspknum><dfsstatus>dfsoff</dfsstatus><protocolver>2.3</protocolver><btmacaddr>yy:yy:yy:yy:yy:yy</btmacaddr></response></UIC>""",

            b"""HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 228
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>VolumeLevel</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier>public</user_identifier><response result="ok"><volume>10</volume></response></UIC>HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 228
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>VolumeLevel</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier>public</user_identifier><response result="ok"><volume>15</volume></response></UIC>HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 228
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>VolumeLevel</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier>public</user_identifier><response result="ok"><volume>20</volume></response></UIC>""",

            b"""HTTP/1.1 200 OK
Date: Fri, 02 Jan 1970 10:53:13 GMT
Server: Samsung/1.0
Content-Type: text/html
Content-Length: 228
Connection: close
Last-Modified: Fri, 02 Jan 1970 10:53:13 GMT

<?xml version="1.0" encoding="UTF-8"?><UIC><method>VolumeLevel</method><version>1.0</version><speakerip>192.168.1.129</speakerip><user_identifier>public</user_identifier><response result="ok"><volume>30</volume></response></UIC>""",
        ]

        expected_responses = [
            {
                'success': True,
                'name': 'RequestDeviceInfo',
            },
            {
                'success': True,
                'name': 'MainInfo',
            },
            {
                'success': True,
                'name': 'VolumeLevel',
            },
            {
                'success': True,
                'name': 'VolumeLevel',
            },
            {
                'success': True,
                'name': 'VolumeLevel',
            },
            {
                'success': True,
                'name': 'VolumeLevel',
            }
        ]

        stream = ApiStream('192.168.1.129')

        responses = list(stream.open('/UIC?cmd=%3Cname%3EGetMainInfo%3C/name%3E'))

        s.return_value.connect.assert_called_once_with(('192.168.1.129', 55001))

        self.assertEqual(len(responses), len(expected_responses))

        for i, response in enumerate(responses):
            self.assertIsInstance(response, ApiResponse)
            self.assertEqual(response.success, expected_responses[i]['success'])
            self.assertEqual(response.name, expected_responses[i]['name'])
