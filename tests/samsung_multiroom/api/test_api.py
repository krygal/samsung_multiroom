import re
import unittest
from unittest.mock import MagicMock

import httpretty
import requests
import xmltodict

from samsung_multiroom.api import COMMAND_CPM
from samsung_multiroom.api import COMMAND_UIC
from samsung_multiroom.api import METHOD_GET
from samsung_multiroom.api import SamsungMultiroomApi
from samsung_multiroom.api import SamsungMultiroomApiException
from samsung_multiroom.api import paginator


class TestApi(unittest.TestCase):

    def test_invalid_method_raises_exception(self):
        api = SamsungMultiroomApi('192.168.1.129', 55001)

        self.assertRaises(ValueError, api.request, 'post', COMMAND_CPM, '<name>GetSpkName</name>')

    def test_invalid_command_raises_exception(self):
        api = SamsungMultiroomApi('192.168.1.129', 55001)

        self.assertRaises(ValueError, api.request, METHOD_GET, 'INVALIDCOMMAND', '<name>GetSpkName</name>')

    @httpretty.activate(allow_net_connect=False)
    def test_request_timeout_raises_exception(self):
        def exception_response():
            raise requests.exceptions.TimeoutException()

        httpretty.register_uri(
            httpretty.GET,
            re.compile(r'http://192.168.1.129:55001/.*'),
            body=exception_response
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        self.assertRaises(SamsungMultiroomApiException, api.request, METHOD_GET, COMMAND_UIC, '<name>GetSpkName</name>')

    @httpretty.activate(allow_net_connect=False)
    def test_request_bad_result_raises_exception(self):
        httpretty.register_uri(
            httpretty.GET,
            re.compile(r'http://192.168.1.129:55001/.*'),
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>SpkName</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ng"></response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        self.assertRaises(SamsungMultiroomApiException, api.request, METHOD_GET, COMMAND_UIC, '<name>GetSpkName</name>')

    @httpretty.activate(allow_net_connect=False)
    def test_request_returns_valid_response(self):
        httpretty.register_uri(
            httpretty.GET,
            re.compile(r'http://192.168.1.129:55001/.*'),
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>SpkName</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <spkname><![CDATA[Living Room]]></spkname>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        response = api.request(METHOD_GET, COMMAND_UIC, '<name>GetSpkName</name>')

        self.assertEqual(response, {
            'spkname': 'Living Room'
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_speaker_name(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetSpkName%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>SpkName</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <spkname><![CDATA[Living Room]]></spkname>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        speaker_name = api.get_speaker_name()

        self.assertEqual(speaker_name, 'Living Room')

    @httpretty.activate(allow_net_connect=False)
    def test_set_speaker_name(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetSpkName%3C/name%3E%3Cp%20type=%22cdata%22%20name=%22spkname%22%20val=%22empty%22%3E%3C![CDATA[Living%20Room]]%3E%3C/p%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>SpkName</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <spkname><![CDATA[Living Room]]></spkname>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        speaker_name = api.set_speaker_name('Living Room')

    @unittest.mock.patch('socket.socket')
    def test_get_main_info(self, s):
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
            b'',
        ]

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        main_info = api.get_main_info()

        self.assertEqual(main_info, {
            'party': 'off',
            'partymain': None,
            'grouptype': 'N',
            'groupmainip': '0.0.0.0',
            'groupmainmacaddr': '00:00:00:00:00:00',
            'spkmacaddr': 'xx:xx:xx:xx:xx:xx',
            'spkmodelname': 'HW-K650',
            'groupmode': 'none',
            'channeltype': 'front',
            'channelvolume': '0',
            'multichinfo': 'on',
            'groupspknum': '1',
            'dfsstatus': 'dfsoff',
            'protocolver': '2.3',
            'btmacaddr': 'yy:yy:yy:yy:yy:yy',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_volume(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetVolume%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>VolumeLevel</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <volume>10</volume>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        volume = api.get_volume()

        self.assertEqual(volume, 10)

    @httpretty.activate(allow_net_connect=False)
    def test_set_volume(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetVolume%3C/name%3E%3Cp%20type=%22dec%22%20name=%22volume%22%20val=%2210%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>VolumeLevel</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <volume>10</volume>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_volume(10)

    @httpretty.activate(allow_net_connect=False)
    def test_get_mute(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetMute%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>MuteStatus</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <mute>off</mute>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        mute = api.get_mute()

        self.assertEqual(mute, False)

    @httpretty.activate(allow_net_connect=False)
    def test_set_mute(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetMute%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22mute%22%20val%3D%22on%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>MuteStatus</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <mute>on</mute>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_mute(True)

    @httpretty.activate(allow_net_connect=False)
    def test_get_func(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetFunc%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>CurrentFunc</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <function>wifi</function>
                        <submode>dlna</submode>
                        <connection></connection>
                        <devicename><![CDATA[]]></devicename>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        func = api.get_func()

        self.assertEqual(func, {
            'function': 'wifi',
            'submode': 'dlna',
            'connection': None,
            'devicename': None,
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_func(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetFunc%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22function%22%20val%3D%22bt%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>PlayStatus</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <function>bt</function>
                        <playstatus>pause</playstatus>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_func('bt')

    @httpretty.activate(allow_net_connect=False)
    def test_get_shuffle_mode(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetShuffleMode%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>ShuffleMode</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <shuffle>on</shuffle>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        shuffle_mode = api.get_shuffle_mode()

        self.assertEqual(shuffle_mode, True)

    @httpretty.activate(allow_net_connect=False)
    def test_set_shuffle_mode(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetShuffleMode%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22shufflemode%22%20val%3D%22on%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>ShuffleMode</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <shuffle>on</shuffle>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_shuffle_mode(True)

    @httpretty.activate(allow_net_connect=False)
    def test_set_trick_mode(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetTrickMode%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22trickmode%22%20val%3D%22next%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>CurrentFunc</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <function>wifi</function>
                        <submode>dlna</submode>
                        <connection></connection>
                        <devicename><![CDATA[]]></devicename>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_trick_mode('next')

    @httpretty.activate(allow_net_connect=False)
    def test_set_playback_control(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetPlaybackControl%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22playbackcontrol%22%20val%3D%22pause%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>PlaybackStatus</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <playstatus>pause</playstatus>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_playback_control('pause')

    @httpretty.activate(allow_net_connect=False)
    def test_get_music_info(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetMusicInfo%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>MusicInfo</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                        <playertype>allshare</playertype>
                        <playbacktype>folder</playbacktype>
                        <sourcename><![CDATA[]]></sourcename>
                        <parentid>22$30224</parentid>
                        <parentid2></parentid2>
                        <playindex>8</playindex>
                        <objectid><![CDATA[22$@52947]]></objectid>
                        <title><![CDATA[New star in the sky]]></title>
                        <artist><![CDATA[Air]]></artist>
                        <album><![CDATA[Moon Safari]]></album>
                        <thumbnail><![CDATA[http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52947.jpg]]></thumbnail>
                        <timelength>0:05:40.000</timelength>
                        <playtime>325067</playtime>
                        <seek>enable</seek>
                        <pause>enable</pause>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        music_info = api.get_music_info()

        self.assertEqual(music_info['title'], 'New star in the sky')
        self.assertEqual(music_info['artist'], 'Air')
        self.assertEqual(music_info['album'], 'Moon Safari')
        self.assertEqual(music_info['thumbnail'], 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52947.jpg')
        self.assertEqual(music_info['timelength'], '0:05:40.000')
        self.assertEqual(music_info['playtime'], '325067')
        self.assertEqual(music_info['seek'], 'enable')
        self.assertEqual(music_info['pause'], 'enable')

    @httpretty.activate(allow_net_connect=False)
    def test_get_play_status(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetPlayStatus%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>PlayStatus</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok">
                        <function>wifi</function>
                        <submode>dlna</submode>
                        <playstatus>play</playstatus>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        func = api.get_play_status()

        self.assertEqual(func, {
            'function': 'wifi',
            'submode': 'dlna',
            'playstatus': 'play',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_search_time(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetSearchTime%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22playtime%22%20val%3D%2250%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>MusicPlayTime</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <timelength>431</timelength>
                        <playtime>50</playtime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_search_time(50)

    @httpretty.activate(allow_net_connect=False)
    def test_get_preset_list(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetPresetList%3C%2Fname%3E%3Cp%20type=%22dec%22%20name=%22startindex%22%20val=%220%22/%3E%3Cp%20type=%22dec%22%20name=%22listcount%22%20val=%2210%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>PresetList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <totallistcount>6</totallistcount>
                        <startindex>0</startindex>
                        <listcount>6</listcount>
                        <timestamp>2018-12-28T17:44:10Z</timestamp>
                        <presetlisttype>0</presetlisttype>
                        <presetlist>
                            <preset>
                                <kind>speaker</kind>
                                <title>Radio Swiss Jazz (Jazz Music)</title>
                                <description>Manu Dibango - Milady&apos;s Song</description>
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s6814t.png</thumbnail>
                                <contentid>0</contentid>
                                <mediaid>s6814</mediaid>
                            </preset>
                            <preset>
                                <kind>speaker</kind>
                                <title>93.5 | BBC Radio 4 (US News)</title>
                                <description>Intelligent speech</description>
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s25419t.png</thumbnail>
                                <contentid>1</contentid>
                                <mediaid>s25419</mediaid>
                            </preset>
                            <preset>
                                <kind>speaker</kind>
                                <title>89.1 | BBC Radio 2 (Adult Hits)</title>
                                <description>Amazing music. Played by an amazing line up.</description>
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s24940t.png</thumbnail>
                                <contentid>2</contentid>
                                <mediaid>s24940</mediaid>
                            </preset>
                            <preset>
                                <kind>my</kind>
                                <title>Radio Swiss Jazz (Jazz Music)</title>
                                <description>Groovin&apos; J 5 - This Here</description>
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s6814t.png</thumbnail>
                                <contentid>3</contentid>
                                <mediaid>s6814</mediaid>
                            </preset>
                            <preset>
                                <kind>my</kind>
                                <title>91.3 | BBC Radio 3 (Classical Music)</title>
                                <description>Live music and arts</description>
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s24941t.png</thumbnail>
                                <contentid>4</contentid>
                                <mediaid>s24941</mediaid>
                            </preset>
                            <preset>
                                <kind>my</kind>
                                <title>93.5 | BBC Radio 4 (US News)</title>
                                <description>Intelligent speech</description>
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s25419t.png</thumbnail>
                                <contentid>5</contentid>
                                <mediaid>s25419</mediaid>
                            </preset>
                        </presetlist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        preset_list = api.get_preset_list(0, 10)

        self.assertEqual(len(preset_list), 6)
        self.assertEqual(preset_list[0]['kind'], 'speaker')
        self.assertEqual(preset_list[0]['title'], 'Radio Swiss Jazz (Jazz Music)')
        self.assertEqual(preset_list[0]['description'], 'Manu Dibango - Milady\'s Song')
        self.assertEqual(preset_list[0]['thumbnail'], 'http://cdn-radiotime-logos.tunein.com/s6814t.png')
        self.assertEqual(preset_list[0]['contentid'], '0')
        self.assertEqual(preset_list[0]['mediaid'], 's6814')

    @httpretty.activate(allow_net_connect=False)
    def test_get_radio_info(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetRadioInfo%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioInfo</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <root>Favorites</root>
                        <presetindex>0</presetindex>
                        <title>Radio Swiss Jazz (Jazz Music)</title>
                        <description>Manu Dibango - Milady&apos;s Song</description>
                        <thumbnail>http://cdn-radiotime-logos.tunein.com/s6814d.png</thumbnail>
                        <mediaid>s6814</mediaid>
                        <allowfeedback>0</allowfeedback>
                        <timestamp>2018-12-28T18:07:07Z</timestamp>
                        <no_queue>1</no_queue>
                        <playstatus>play</playstatus>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        func = api.get_radio_info()

        self.assertEqual(func, {
            'cpname': 'TuneIn',
            'root': 'Favorites',
            'presetindex': '0',
            'title': 'Radio Swiss Jazz (Jazz Music)',
            'description': 'Manu Dibango - Milady\'s Song',
            'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s6814d.png',
            'mediaid': 's6814',
            'allowfeedback': '0',
            'timestamp': '2018-12-28T18:07:07Z',
            'no_queue': '1',
            'playstatus': 'play',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_play_preset(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetPlayPreset%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22presettype%22%20val%3D%221%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22presetindex%22%20val%3D%220%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>StopPlaybackEvent</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <playtime>0</playtime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_play_preset(1, 0)

    @httpretty.activate(allow_net_connect=False)
    def test_set_select_radio(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetSelectRadio%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioSelected</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <signinstatus>0</signinstatus>
                        <timestamp>2018-12-28T18:35:17Z</timestamp>
                        <audioinfo>
                            <title>Radio Swiss Jazz (Jazz Music)</title>
                            <thumbnail>http://cdn-radiotime-logos.tunein.com/s6814d.png</thumbnail>
                            <playstatus>play</playstatus>
                        </audioinfo>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_select_radio()

    @httpretty.activate(allow_net_connect=False)
    def test_get_dms_list(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetDmsList%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22liststartindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2220%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>DmsList</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <listtotalcount>1</listtotalcount>
                        <liststartindex>0</liststartindex>
                        <listcount>1</listcount>
                        <dmslist>
                            <dms device_id="0">
                                <dmsid>uuid:00113249-398f-0011-8f39-8f3949321100</dmsid>
                                <dmsname><![CDATA[nas]]></dmsname>
                                <devicetype>network</devicetype>
                                <thumbnail_PNG_LRG><![CDATA[http://192.168.1.111:50001/tmp_icon/dmsicon120.png]]></thumbnail_PNG_LRG>
                                <thumbnail_JPG_LRG><![CDATA[http://192.168.1.111:50001/tmp_icon/dmsicon120.jpg]]></thumbnail_JPG_LRG>
                                <thumbnail_PNG_SM><![CDATA[http://192.168.1.111:50001/tmp_icon/dmsicon48.png]]></thumbnail_PNG_SM>
                                <thumbnail_JPG_SM><![CDATA[http://192.168.1.111:50001/tmp_icon/dmsicon48.jpg]]></thumbnail_JPG_SM>
                            </dms>
                        </dmslist>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        dms_list = api.get_dms_list(0, 20)

        self.assertEqual(len(dms_list), 1)
        self.assertEqual(dms_list[0], {
            '@device_id': '0',
            'dmsid': 'uuid:00113249-398f-0011-8f39-8f3949321100',
            'dmsname': 'nas',
            'devicetype': 'network',
            'thumbnail_PNG_LRG': 'http://192.168.1.111:50001/tmp_icon/dmsicon120.png',
            'thumbnail_JPG_LRG': 'http://192.168.1.111:50001/tmp_icon/dmsicon120.jpg',
            'thumbnail_PNG_SM': 'http://192.168.1.111:50001/tmp_icon/dmsicon48.png',
            'thumbnail_JPG_SM': 'http://192.168.1.111:50001/tmp_icon/dmsicon48.jpg',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_pc_get_music_list_by_category(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EPCGetMusicListByCategory%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22device_udn%22%20val%3D%22uuid%3A00113249-398f-0011-8f39-8f3949321100%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22filter%22%20val%3D%22folder%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22categoryid%22%20val%3D%22folder%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22liststartindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2220%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>PCMusicList</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <listtotalcount>3</listtotalcount>
                        <liststartindex>0</liststartindex>
                        <listcount>3</listcount>
                        <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                        <filter>folder</filter>
                        <playertype>myphone</playertype>
                        <playbacktype>playlist</playbacktype>
                        <sourcename><![CDATA[nas]]></sourcename>
                        <parentid>0</parentid>
                        <parentid2 />
                        <musiclist>
                            <music object_id="21">
                                <type>CONTAINER</type>
                                <playindex>-1</playindex>
                                <name />
                                <title><![CDATA[Music]]></title>
                                <artist />
                                <album />
                                <thumbnail />
                                <timelength />
                                <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                            </music>
                            <music object_id="37">
                                <type>CONTAINER</type>
                                <playindex>-1</playindex>
                                <name />
                                <title><![CDATA[Photo]]></title>
                                <artist />
                                <album />
                                <thumbnail />
                                <timelength />
                                <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                            </music>
                            <music object_id="44">
                                <type>CONTAINER</type>
                                <playindex>-1</playindex>
                                <name />
                                <title><![CDATA[Video]]></title>
                                <artist />
                                <album />
                                <thumbnail />
                                <timelength />
                                <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                            </music>
                        </musiclist>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        music_list = api.pc_get_music_list_by_category('uuid:00113249-398f-0011-8f39-8f3949321100', 0, 20)

        self.assertEqual(len(music_list), 3)
        self.assertEqual(music_list[0], {
            '@object_id': '21',
            'type': 'CONTAINER',
            'playindex': '-1',
            'name': None,
            'title': 'Music',
            'artist': None,
            'album': None,
            'thumbnail': None,
            'timelength': None,
            'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_pc_get_music_list_by_id(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EPCGetMusicListByID%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22device_udn%22%20val%3D%22uuid%3A00113249-398f-0011-8f39-8f3949321100%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22filter%22%20val%3D%22folder%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22parentid%22%20val%3D%2222%2430224%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22liststartindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2220%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>PCMusicList</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <listtotalcount>2</listtotalcount>
                        <liststartindex>0</liststartindex>
                        <listcount>2</listcount>
                        <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                        <filter>folder</filter>
                        <playertype>myphone</playertype>
                        <playbacktype>playlist</playbacktype>
                        <sourcename><![CDATA[nas]]></sourcename>
                        <parentid>22$30224</parentid>
                        <parentid2 />
                        <musiclist>
                            <music object_id="22$@52941">
                                <type>AUDIO</type>
                                <playindex>0</playindex>
                                <name><![CDATA[La femme d'argent.mp3]]></name>
                                <title><![CDATA[La femme d'argent]]></title>
                                <artist><![CDATA[Air]]></artist>
                                <album><![CDATA[Moon Safari]]></album>
                                <thumbnail><![CDATA[http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52941.jpg]]></thumbnail>
                                <timelength>0:07:11.000</timelength>
                                <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                            </music>
                            <music object_id="22$@52942">
                                <type>AUDIO</type>
                                <playindex>1</playindex>
                                <name><![CDATA[Sexy boy.mp3]]></name>
                                <title><![CDATA[Sexy boy]]></title>
                                <artist><![CDATA[Air]]></artist>
                                <album><![CDATA[Moon Safari]]></album>
                                <thumbnail><![CDATA[http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52942.jpg]]></thumbnail>
                                <timelength>0:04:58.000</timelength>
                                <device_udn>uuid:00113249-398f-0011-8f39-8f3949321100</device_udn>
                            </music>
                        </musiclist>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        music_list = api.pc_get_music_list_by_id('uuid:00113249-398f-0011-8f39-8f3949321100', '22$30224', 0, 20)

        self.assertEqual(len(music_list), 2)
        self.assertEqual(music_list[0], {
            '@object_id': '22$@52941',
            'type': 'AUDIO',
            'playindex': '0',
            'name': 'La femme d\'argent.mp3',
            'title': 'La femme d\'argent',
            'artist': 'Air',
            'album': 'Moon Safari',
            'thumbnail': 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52941.jpg',
            'timelength': '0:07:11.000',
            'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_playlist_playback_control(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetPlaylistPlaybackControl%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22playbackcontrol%22%20val%3D%22play%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22playertype%22%20val%3D%22allshare%22/%3E%3Cp%20type%3D%22cdata%22%20name%3D%22sourcename%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5B%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22dec%22%20name%3D%22playindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22playtime%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22totalobjectcount%22%20val%3D%221%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22device_udn%22%20val%3D%22uuid%3A00113249-398f-0011-8f39-8f3949321100%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22objectid%22%20val%3D%2222%24%4052942%22/%3E%3Cp%20type%3D%22cdata%22%20name%3D%22songtitle%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5BSexy%20boy%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22cdata%22%20name%3D%22thumbnail%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5Bhttp%3A//192.168.1.111%3A50002/transcoder/jpegtnscaler.cgi/folderart/52941.jpg%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22cdata%22%20name%3D%22artist%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5BAir%5D%5D%3E%3C/p%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>StopPlaybackEvent</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <playtime>0</playtime>
                    </response>
                </UIC>"""
        )

        items = [
            {
                'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
                'object_id': '22$@52942',
                'title': 'Sexy boy',
                'thumbnail': 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52941.jpg',
                'artist': 'Air',
            }
        ]

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_playlist_playback_control(items)

    @httpretty.activate(allow_net_connect=False)
    def test_browse_main(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EBrowseMain%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22startindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2230%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <root>Browse</root>
                        <browsemode>0</browsemode>
                        <category isroot="1">Browse</category>
                        <totallistcount>4</totallistcount>
                        <startindex>0</startindex>
                        <listcount>4</listcount>
                        <timestamp>2018-12-31T16:06:37Z</timestamp>
                        <menulist>
                            <menuitem type="0">
                                <title>Favorites</title>
                                <contentid>0</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Local Radio</title>
                                <contentid>1</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Recents</title>
                                <contentid>2</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Trending</title>
                                <contentid>3</contentid>
                            </menuitem>
                        </menulist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        items = api.browse_main(0, 30)

        self.assertEqual(len(items), 4)
        self.assertEqual(items[0], {
            '@type': '0',
            'title': 'Favorites',
            'contentid': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_select_radio_list_with_folders(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetSelectRadioList%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22contentid%22%20val%3D%2210%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22startindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2230%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <root>Browse</root>
                        <browsemode>0</browsemode>
                        <category isroot="0">By Language</category>
                        <totallistcount>4</totallistcount>
                        <startindex>0</startindex>
                        <listcount>4</listcount>
                        <timestamp>2018-12-31T16:23:16Z</timestamp>
                        <menulist>
                            <menuitem type="0">
                                <title>Aboriginal</title>
                                <contentid>0</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Afrikaans</title>
                                <contentid>1</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Akan</title>
                                <contentid>2</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Albanian</title>
                                <contentid>3</contentid>
                            </menuitem>
                        </menulist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        items = api.get_select_radio_list(10, 0, 30)

        self.assertEqual(len(items), 4)
        self.assertEqual(items[0], {
            '@type': '0',
            'title': 'Aboriginal',
            'contentid': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_select_radio_list_with_radios(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetSelectRadioList%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22contentid%22%20val%3D%223%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22startindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2230%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <root>Browse</root>
                        <browsemode>0</browsemode>
                        <category isroot="0">Trending</category>
                        <totallistcount>4</totallistcount>
                        <startindex>0</startindex>
                        <listcount>4</listcount>
                        <timestamp>2018-12-31T16:30:03Z</timestamp>
                        <menulist>
                            <menuitem type="2">
                                <thumbnail>http://cdn-profiles.tunein.com/s297990/images/logot.png</thumbnail>
                                <description>MSNBC Live with Velshi &amp; Ruhle</description>
                                <mediaid>s297990</mediaid>
                                <title>MSNBC</title>
                                <contentid>0</contentid>
                            </menuitem>
                            <menuitem type="2">
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s24940t.png</thumbnail>
                                <description>Amazing music. Played by an amazing line up.</description>
                                <mediaid>s24940</mediaid>
                                <title>BBC Radio 2</title>
                                <contentid>1</contentid>
                            </menuitem>
                            <menuitem type="2">
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s17077t.png</thumbnail>
                                <description>Drive with Adrian Durham &amp; Matt Holland</description>
                                <mediaid>s17077</mediaid>
                                <title>talkSPORT</title>
                                <contentid>2</contentid>
                            </menuitem>
                            <menuitem type="2">
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s24939t.png</thumbnail>
                                <description>The best new music</description>
                                <mediaid>s24939</mediaid>
                                <title>BBC Radio 1</title>
                                <contentid>3</contentid>
                            </menuitem>
                        </menulist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        items = api.get_select_radio_list(3, 0, 30)

        self.assertEqual(len(items), 4)
        self.assertEqual(items[0], {
            '@type': '2',
            'thumbnail': 'http://cdn-profiles.tunein.com/s297990/images/logot.png',
            'description': 'MSNBC Live with Velshi & Ruhle',
            'mediaid': 's297990',
            'title': 'MSNBC',
            'contentid': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_current_radio_list(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetCurrentRadioList%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22startindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2230%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <root>Browse</root>
                        <browsemode>0</browsemode>
                        <category isroot="0">Trending</category>
                        <totallistcount>4</totallistcount>
                        <startindex>0</startindex>
                        <listcount>4</listcount>
                        <timestamp>2018-12-31T16:30:03Z</timestamp>
                        <menulist>
                            <menuitem type="2">
                                <thumbnail>http://cdn-profiles.tunein.com/s297990/images/logot.png</thumbnail>
                                <description>MSNBC Live with Velshi &amp; Ruhle</description>
                                <mediaid>s297990</mediaid>
                                <title>MSNBC</title>
                                <contentid>0</contentid>
                            </menuitem>
                            <menuitem type="2">
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s24940t.png</thumbnail>
                                <description>Amazing music. Played by an amazing line up.</description>
                                <mediaid>s24940</mediaid>
                                <title>BBC Radio 2</title>
                                <contentid>1</contentid>
                            </menuitem>
                            <menuitem type="2">
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s17077t.png</thumbnail>
                                <description>Drive with Adrian Durham &amp; Matt Holland</description>
                                <mediaid>s17077</mediaid>
                                <title>talkSPORT</title>
                                <contentid>2</contentid>
                            </menuitem>
                            <menuitem type="2">
                                <thumbnail>http://cdn-radiotime-logos.tunein.com/s24939t.png</thumbnail>
                                <description>The best new music</description>
                                <mediaid>s24939</mediaid>
                                <title>BBC Radio 1</title>
                                <contentid>3</contentid>
                            </menuitem>
                        </menulist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        items = api.get_current_radio_list(0, 30)

        self.assertEqual(len(items), 4)
        self.assertEqual(items[0], {
            '@type': '2',
            'thumbnail': 'http://cdn-profiles.tunein.com/s297990/images/logot.png',
            'description': 'MSNBC Live with Velshi & Ruhle',
            'mediaid': 's297990',
            'title': 'MSNBC',
            'contentid': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_upper_radio_list(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetUpperRadioList%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22startindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2230%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <root>Browse</root>
                        <browsemode>0</browsemode>
                        <category isroot="0">By Language</category>
                        <totallistcount>4</totallistcount>
                        <startindex>0</startindex>
                        <listcount>4</listcount>
                        <timestamp>2018-12-31T16:23:16Z</timestamp>
                        <menulist>
                            <menuitem type="0">
                                <title>Aboriginal</title>
                                <contentid>0</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Afrikaans</title>
                                <contentid>1</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Akan</title>
                                <contentid>2</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Albanian</title>
                                <contentid>3</contentid>
                            </menuitem>
                        </menulist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        items = api.get_upper_radio_list(0, 30)

        self.assertEqual(len(items), 4)
        self.assertEqual(items[0], {
            '@type': '0',
            'title': 'Aboriginal',
            'contentid': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_play_select_single(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetPlaySelect%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22selectitemid%22%20val%3D%220%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>StopPlaybackEvent</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <playtime>131</playtime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_play_select('0')

    @httpretty.activate(allow_net_connect=False)
    def test_set_play_select_multiple(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetPlaySelect%3C/name%3E%3Cp%20type%3D%22dec_arr%22%20name%3D%22selectitemids%22%20val%3D%22empty%22%3E%3Citem%3E1%3C/item%3E%3Citem%3E2%3C/item%3E%3Citem%3E3%3C/item%3E%3C/p%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>StopPlaybackEvent</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <playtime>131</playtime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_play_select(['1', '2', '3'])

    @httpretty.activate(allow_net_connect=False)
    def test_get_station_data(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetStationData%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22selectitemid%22%20val%3D%223%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>StationData</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>TuneIn</cpname>
                        <title>BBC Radio 2</title>
                        <browsemode>0</browsemode>
                        <description>Amazing music. Played by an amazing line up.</description>
                        <thumbnail>http://cdn-radiotime-logos.tunein.com/s24940d.png</thumbnail>
                        <stationurl>http://opml.radiotime.com/Tune.ashx?id=s24940&amp;partnerId=qDDAbg6M&amp;serial=14BB6E87BBDB&amp;formats=mp3,wma,aac,qt,hls</stationurl>
                        <timestamp>2019-01-08T15:21:47Z</timestamp>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        station_data = api.get_station_data(3)

        self.assertEqual(station_data, {
            'cpname': 'TuneIn',
            'title': 'BBC Radio 2',
            'browsemode': '0',
            'description': 'Amazing music. Played by an amazing line up.',
            'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s24940d.png',
            'stationurl': 'http://opml.radiotime.com/Tune.ashx?id=s24940&partnerId=qDDAbg6M&serial=14BB6E87BBDB&formats=mp3,wma,aac,qt,hls',
            'timestamp': '2019-01-08T15:21:47Z',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_7band_eq_list(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGet7BandEQList%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>7BandEQList</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <listcount>5</listcount>
                        <presetlistcount>4</presetlistcount>
                        <presetlist>
                            <preset index="0">
                                <presetindex>0</presetindex>
                                <presetname>None</presetname>
                            </preset>
                            <preset index="1">
                                <presetindex>1</presetindex>
                                <presetname>Pop</presetname>
                            </preset>
                            <preset index="2">
                                <presetindex>2</presetindex>
                                <presetname>Jazz</presetname>
                            </preset>
                            <preset index="3">
                                <presetindex>3</presetindex>
                                <presetname>Classic</presetname>
                            </preset>
                            <preset index="4">
                                <presetindex>4</presetindex>
                                <presetname>customtitle</presetname>
                            </preset>
                        </presetlist>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        presets = api.get_7band_eq_list()

        self.assertEqual(len(presets), 5)
        self.assertEqual(presets[0], {
            '@index': '0',
            'presetindex': '0',
            'presetname': 'None'
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_current_eq_mode(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetCurrentEQMode%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>CurrentEQMode</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <presetindex>3</presetindex>
                        <presetname>Classic</presetname>
                        <eqvalue1>2</eqvalue1>
                        <eqvalue2>0</eqvalue2>
                        <eqvalue3>0</eqvalue3>
                        <eqvalue4>5</eqvalue4>
                        <eqvalue5>0</eqvalue5>
                        <eqvalue6>1</eqvalue6>
                        <eqvalue7>0</eqvalue7>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        equalizer = api.get_current_eq_mode()

        self.assertEqual(equalizer, {
            'presetindex': '3',
            'presetname': 'Classic',
            'eqvalue1': '2',
            'eqvalue2': '0',
            'eqvalue3': '0',
            'eqvalue4': '5',
            'eqvalue5': '0',
            'eqvalue6': '1',
            'eqvalue7': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_7band_eq_value(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESet7bandEQValue%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22presetindex%22%20val%3D%224%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue1%22%20val%3D%221%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue2%22%20val%3D%222%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue3%22%20val%3D%223%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue4%22%20val%3D%224%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue5%22%20val%3D%225%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue6%22%20val%3D%226%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue7%22%20val%3D%22-6%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>7bandEQValue</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <presetindex>4</presetindex>
                        <eqvalue1>1</eqvalue1>
                        <eqvalue2>2</eqvalue2>
                        <eqvalue3>3</eqvalue3>
                        <eqvalue4>4</eqvalue4>
                        <eqvalue5>5</eqvalue5>
                        <eqvalue6>6</eqvalue6>
                        <eqvalue7>-6</eqvalue7>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_7band_eq_value(4, [1,2,3,4,5,6,-6])

    @httpretty.activate(allow_net_connect=False)
    def test_set_7band_eq_mode(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESet7bandEQMode%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22presetindex%22%20val%3D%221%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>7bandEQMode</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <presetindex>1</presetindex>
                        <presetname>Pop</presetname>
                        <eqvalue1>0</eqvalue1>
                        <eqvalue2>-3</eqvalue2>
                        <eqvalue3>3</eqvalue3>
                        <eqvalue4>1</eqvalue4>
                        <eqvalue5>-5</eqvalue5>
                        <eqvalue6>0</eqvalue6>
                        <eqvalue7>0</eqvalue7>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_7band_eq_mode(1)

    @httpretty.activate(allow_net_connect=False)
    def test_reset_7band_eq_value(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EReset7bandEQValue%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22presetindex%22%20val%3D%221%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue1%22%20val%3D%221%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue2%22%20val%3D%222%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue3%22%20val%3D%223%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue4%22%20val%3D%224%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue5%22%20val%3D%225%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue6%22%20val%3D%226%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22eqvalue7%22%20val%3D%22-6%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>Reset7bandEQValue</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <presetindex>1</presetindex>
                        <eqvalue1>1</eqvalue1>
                        <eqvalue2>2</eqvalue2>
                        <eqvalue3>3</eqvalue3>
                        <eqvalue4>4</eqvalue4>
                        <eqvalue5>5</eqvalue5>
                        <eqvalue6>6</eqvalue6>
                        <eqvalue7>-6</eqvalue7>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.reset_7band_eq_value(1, [1,2,3,4,5,6,-6])

    @httpretty.activate(allow_net_connect=False)
    def test_del_custom_eq_mode(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EDelCustomEQMode%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22presetindex%22%20val%3D%225%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>DelCustomEQMode</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <presetindex>5</presetindex>
                        <presetname>Custom 2</presetname>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.del_custom_eq_mode(5)

    @httpretty.activate(allow_net_connect=False)
    def test_add_custom_eq_mode(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EAddCustomEQMode%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22presetindex%22%20val%3D%225%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22presetname%22%20val%3D%22my%20custom%20preset%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>AddCustomEQMode</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <presetindex>5</presetindex>
                        <presetname>my custom preset</presetname>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.add_custom_eq_mode(5, 'my custom preset')

    @httpretty.activate(allow_net_connect=False)
    def test_set_speaker_time(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetSpeakerTime%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22year%22%20val%3D%222019%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22month%22%20val%3D%221%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22day%22%20val%3D%226%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22hour%22%20val%3D%2212%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22min%22%20val%3D%2255%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22sec%22%20val%3D%2224%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>SpeakerTime</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <year>2019</year>
                        <month>1</month>
                        <day>6</day>
                        <hour>12</hour>
                        <min>55</min>
                        <sec>24</sec>
                    </response>
                </UIC>"""
        )

        import datetime

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_speaker_time(datetime.datetime(2019, 1, 6, 12, 55, 24))

    @httpretty.activate(allow_net_connect=False)
    def test_get_sleep_timer(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetSleepTimer%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>SleepTime</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <sleepoption>off</sleepoption>
                        <sleeptime>0</sleeptime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        timer = api.get_sleep_timer()

        self.assertEqual(timer, {
            'sleepoption': 'off',
            'sleeptime': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_sleep_timer(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetSleepTimer%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22option%22%20val%3D%22start%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22sleeptime%22%20val%3D%22300%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>SleepTime</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <sleepoption>start</sleepoption>
                        <sleeptime>300</sleeptime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_sleep_timer('start', 300)

    @httpretty.activate(allow_net_connect=False)
    def test_get_alarm_info(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetAlarmInfo%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>AllAlarmInfo</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <totalindexcount>2</totalindexcount>
                        <alarmList>
                            <alarm index="0">
                                <hour>13</hour>
                                <min>27</min>
                                <week>0x40</week>
                                <volume>20</volume>
                                <title />
                                <description />
                                <thumbnail />
                                <stationurl />
                                <set>on</set>
                                <soundenable>on</soundenable>
                                <sound>1</sound>
                                <alarmsoundname>Disco</alarmsoundname>
                                <duration>10</duration>
                            </alarm>
                            <alarm index="1">
                                <hour>14</hour>
                                <min>25</min>
                                <week>0x28</week>
                                <volume>6</volume>
                                <title><![CDATA[MSNBC]]></title>
                                <description><![CDATA[MSNBC is the premier...]]></description>
                                <thumbnail />
                                <stationurl><![CDATA[http://]]></stationurl>
                                <set>on</set>
                                <soundenable>off</soundenable>
                                <sound>-1</sound>
                                <alarmsoundname />
                                <duration>0</duration>
                            </alarm>
                        </alarmList>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        alarm_info = api.get_alarm_info()

        self.assertEqual(len(alarm_info), 2)
        self.assertEqual(alarm_info[0], {
            '@index': '0',
            'hour': '13',
            'min': '27',
            'week': '0x40',
            'volume': '20',
            'title': None,
            'description': None,
            'thumbnail': None,
            'stationurl': None,
            'set': 'on',
            'soundenable': 'on',
            'sound': '1',
            'alarmsoundname': 'Disco',
            'duration': '10',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_alarm_on_off(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetAlarmOnOff%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22index%22%20val%3D%220%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22alarm%22%20val%3D%22on%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>AlarmOnOff</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <index>0</index>
                        <alarm>on</alarm>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_alarm_on_off(0, 'on')

    @httpretty.activate(allow_net_connect=False)
    def test_get_alarm_sound_list(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetAlarmSoundList%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>AlarmSoundList</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <listcount>4</listcount>
                        <alarmlist>
                            <alarmsound index="0">
                                <alarsoundindex>0</alarsoundindex>
                                <alarmsoundname>Active Morning</alarmsoundname>
                            </alarmsound>
                            <alarmsound index="1">
                                <alarsoundindex>1</alarsoundindex>
                                <alarmsoundname>Disco</alarmsoundname>
                            </alarmsound>
                            <alarmsound index="2">
                                <alarsoundindex>2</alarsoundindex>
                                <alarmsoundname>Vintage</alarmsoundname>
                            </alarmsound>
                            <alarmsound index="3">
                                <alarsoundindex>3</alarsoundindex>
                                <alarmsoundname>Waltz</alarmsoundname>
                            </alarmsound>
                        </alarmlist>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        sounds = api.get_alarm_sound_list()

        self.assertEqual(len(sounds), 4)
        self.assertEqual(sounds[0], {
            '@index': '0',
            'alarsoundindex': '0',
            'alarmsoundname': 'Active Morning',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_alarm_info(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetAlarmInfo%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22index%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22hour%22%20val%3D%2218%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22min%22%20val%3D%2221%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22week%22%20val%3D%220x1c%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22volume%22%20val%3D%222%22/%3E%3Cp%20type%3D%22cdata%22%20name%3D%22title%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5BBBC%20Radio%204%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22cdata%22%20name%3D%22description%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5BIntelligent%20speech%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22cdata%22%20name%3D%22thumbnail%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5Bhttp%3A//cdn-radiotime-logos.tunein.com/s25419d.png%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22cdata%22%20name%3D%22stationurl%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5Bhttp%3A//opml.radiotime.com/Tune.ashx%3Fid%3Ds25419%26partnerId%3DqDDAbg6M%26serial%3D90F1AAD31D82%26formats%3Dmp3%2Cwma%2Caac%2Cqt%2Chls%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22str%22%20name%3D%22soundenable%22%20val%3D%22off%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22sound%22%20val%3D%22-1%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22duration%22%20val%3D%220%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>AlarmInfo</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <index>0</index>
                        <hour>18</hour>
                        <min>21</min>
                        <week>0x1c</week>
                        <volume>2</volume>
                        <title><![CDATA[BBC Radio 4]]></title>
                        <description><![CDATA[Intelligent speech]]></description>
                        <thumbnail><![CDATA[http://cdn-radiotime-logos.tunein.com/s25419d.png]]></thumbnail>
                        <stationurl><![CDATA[http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls]]></stationurl>
                        <alarm>on</alarm>
                        <soundenable>off</soundenable>
                        <sound>-1</sound>
                        <duration>0</duration>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_alarm_info(
            index=0,
            hour=18,
            minute=21,
            week='0x1C',
            duration=0,
            volume=2,
            station_data={
                'title': 'BBC Radio 4',
                'description': 'Intelligent speech',
                'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s25419d.png',
                'stationurl': 'http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls',
            }
        )

    @httpretty.activate(allow_net_connect=False)
    def test_del_alarm(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EDelAlarm%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22totaldelnum%22%20val%3D%224%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22index%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22index%22%20val%3D%221%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22index%22%20val%3D%222%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22index%22%20val%3D%224%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>DelAlarm</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier />
                    <response result="ok">
                        <index>0</index>
                        <index>1</index>
                        <index>2</index>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.del_alarm([0, 1, 2, 4])

    @unittest.skip('API call doesn\'t give any response')
    def test_spk_in_group(self):
        api = SamsungMultiroomApi(ip, 55001)
        api.spk_in_group('select')

    @httpretty.activate(allow_net_connect=False)
    def test_set_multispk_group(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetMultispkGroup%3C/name%3E%3Cp%20type%3D%22cdata%22%20name%3D%22name%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5BTest%20group%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22dec%22%20name%3D%22index%22%20val%3D%221%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22type%22%20val%3D%22main%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22spknum%22%20val%3D%223%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22audiosourcemacaddr%22%20val%3D%2200%3A00%3A00%3A00%3A00%3A00%22/%3E%3Cp%20type%3D%22cdata%22%20name%3D%22audiosourcename%22%20val%3D%22empty%22%3E%3C%21%5BCDATA%5BLiving%20Room%5D%5D%3E%3C/p%3E%3Cp%20type%3D%22str%22%20name%3D%22audiosourcetype%22%20val%3D%22speaker%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22subspkip%22%20val%3D%22192.168.1.165%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22subspkmacaddr%22%20val%3D%2211%3A11%3A11%3A11%3A11%3A11%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22subspkip%22%20val%3D%22192.168.1.216%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22subspkmacaddr%22%20val%3D%2222%3A22%3A22%3A22%3A22%3A22%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>MultispkGroupStartEvent</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <groupname><![CDATA[Test group]]></groupname>
                        <grouptype>M</grouptype>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_multispk_group('Test group', [
            {
                'name': 'Living Room',
                'ip': '192.168.1.129',
                'mac': '00:00:00:00:00:00',
            },
            {
                'name': 'Kitchen',
                'ip': '192.168.1.165',
                'mac': '11:11:11:11:11:11',
            },
            {
                'name': 'Bedroom',
                'ip': '192.168.1.216',
                'mac': '22:22:22:22:22:22',
            }
        ])

    @httpretty.activate(allow_net_connect=False)
    def test_set_ungroup(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3ESetUngroup%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>Ungroup</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok" />
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_ungroup()

    @httpretty.activate(allow_net_connect=False)
    def test_get_cp_list(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetCpList%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22liststartindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2230%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>CpList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <listtotalcount>24</listtotalcount>
                        <liststartindex>0</liststartindex>
                        <listcount>24</listcount>
                        <cplist>
                            <cp>
                                <cpid>0</cpid>
                                <cpname>Pandora</cpname>
                                <signinstatus>0</signinstatus>
                            </cp>
                            <cp>
                                <cpid>1</cpid>
                                <cpname>Spotify</cpname>
                                <signinstatus>0</signinstatus>
                            </cp>
                            <cp>
                                <cpid>2</cpid>
                                <cpname>Deezer</cpname>
                                <signinstatus>1</signinstatus>
                                <username>test_username</username>
                            </cp>
                        </cplist>
                    </response>
                    </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        cps = api.get_cp_list(0, 30)

        self.assertEqual(len(cps), 3)
        self.assertEqual(cps[0], {
            'cpid': '0',
            'cpname': 'Pandora',
            'signinstatus': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_cp_service(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetCpService%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22cpservice_id%22%20val%3D%222%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="utf-8" ?>
                <CPM>
                    <method>CpChanged</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_cp_service(2)

    @httpretty.activate(allow_net_connect=False)
    def test_get_cp_info(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetCpInfo%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>CpInfo</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                        <timestamp>2019-01-14T09:50:46Z</timestamp>
                        <category />
                        <signinstatus>1</signinstatus>
                        <username>test_username</username>
                        <subscription_info>Listening is limited to 30-second clips. Subscribe to enjoy unlimited music!</subscription_info>
                        <audioinfo>
                            <title>Introduction And Yaqui Indian Folk Song</title>
                            <streamtype>station</streamtype>
                            <thumbnail>https://e-cdns-images.dzcdn.net/images/cover/a9b4964ab775575efa2719827b9e88b9/500x500-000000-80-0-0.jpg</thumbnail>
                            <playstatus>play</playstatus>
                        </audioinfo>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        cp_info = api.get_cp_info()

        self.assertEqual(cp_info, {
            'cpname': 'Deezer',
            'timestamp': '2019-01-14T09:50:46Z',
            'category': None,
            'signinstatus': '1',
            'username': 'test_username',
            'subscription_info': 'Listening is limited to 30-second clips. Subscribe to enjoy unlimited music!',
            'audioinfo': {
                'title': 'Introduction And Yaqui Indian Folk Song',
                'streamtype': 'station',
                'thumbnail': 'https://e-cdns-images.dzcdn.net/images/cover/a9b4964ab775575efa2719827b9e88b9/500x500-000000-80-0-0.jpg',
                'playstatus': 'play',
            },
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_sign_in(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetSignIn%3C/name%3E%3Cp%20type%3D%22str%22%20name%3D%22username%22%20val%3D%22test_username%22/%3E%3Cp%20type%3D%22str%22%20name%3D%22password%22%20val%3D%22test_password%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>SignInStatus</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                        <timestamp>2019-01-14T10:09:49Z</timestamp>
                        <category isroot="1" />
                        <category_localized />
                        <signinstatus>1</signinstatus>
                        <root>Playlist Picks</root>
                        <root_index>2</root_index>
                        <root_localized>Playlist Picks</root_localized>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_sign_in('test_username', 'test_password')

    @httpretty.activate(allow_net_connect=False)
    def test_set_sign_out(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetSignOut%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>SignOutStatus</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                        <timestamp>2019-01-14T10:17:05Z</timestamp>
                        <category isroot="1" />
                        <category_localized />
                        <signoutstatus>1</signoutstatus>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_sign_out()

    @httpretty.activate(allow_net_connect=False)
    def test_get_cp_submenu(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetCpSubmenu%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>SubMenu</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                        <timestamp>2019-01-14T10:23:16Z</timestamp>
                        <totallistcount>10</totallistcount>
                        <submenu selected_id="0">
                            <submenuitem id="0">
                                <submenuitem_localized><![CDATA[Flow]]></submenuitem_localized>
                            </submenuitem>
                            <submenuitem id="1">
                                <submenuitem_localized><![CDATA[Browse]]></submenuitem_localized>
                            </submenuitem>
                            <submenuitem id="2">
                                <submenuitem_localized><![CDATA[Playlist Picks]]></submenuitem_localized>
                            </submenuitem>
                        </submenu>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        submenu = api.get_cp_submenu()

        self.assertEqual(len(submenu), 3)
        self.assertEqual(submenu[0], {
            '@id': '0',
            'submenuitem_localized': 'Flow',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_select_cp_submenu(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetSelectCpSubmenu%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22contentid%22%20val%3D%221%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22startindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2210%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                        <timestamp>2019-01-14T10:40:56Z</timestamp>
                        <root>Browse</root>
                        <root_index>1</root_index>
                        <root_localized>Browse</root_localized>
                        <category isroot="1">Genres</category>
                        <category_localized>Genres</category_localized>
                        <totallistcount>23</totallistcount>
                        <startindex>0</startindex>
                        <listcount>10</listcount>
                        <menulist>
                            <menuitem type="0">
                                <title>All</title>
                                <contentid>0</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Pop</title>
                                <contentid>1</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Rap/Hip Hop</title>
                                <contentid>2</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Rock</title>
                                <contentid>3</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Dance</title>
                                <contentid>4</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>R&amp;B</title>
                                <contentid>5</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Alternative</title>
                                <contentid>6</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Electro</title>
                                <contentid>7</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Folk</title>
                                <contentid>8</contentid>
                            </menuitem>
                            <menuitem type="0">
                                <title>Reggae</title>
                                <contentid>9</contentid>
                            </menuitem>
                        </menulist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        submenu = api.set_select_cp_submenu(1, 0, 10)

        self.assertEqual(len(submenu), 10)
        self.assertEqual(submenu[0], {
            '@type': '0',
            'title': 'All',
            'contentid': '0',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_get_cp_player_playlist(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3EGetCpPlayerPlaylist%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22startindex%22%20val%3D%220%22/%3E%3Cp%20type%3D%22dec%22%20name%3D%22listcount%22%20val%3D%2230%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>RadioPlayList</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                        <timestamp>2019-01-14T11:10:39Z</timestamp>
                        <root>Playlist Picks</root>
                        <root_index>2</root_index>
                        <root_localized>Playlist Picks</root_localized>
                        <category isroot="0">Playlist</category>
                        <category_localized>Playlist</category_localized>
                        <totallistcount>3</totallistcount>
                        <startindex>0</startindex>
                        <listcount>3</listcount>
                        <menulist>
                            <menuitem type="1" available="1" currentplaying="1">
                                <artist>Madeleine Peyroux</artist>
                                <album>Careless Love</album>
                                <mediaid>881851</mediaid>
                                <tracklength>0</tracklength>
                                <title>Don't Wait Too Long</title>
                                <contentid>0</contentid>
                                <thumbnail>http://api.deezer.com/album/100127/image</thumbnail>
                            </menuitem>
                            <menuitem type="1" available="1">
                                <artist>Marcus Strickland's Twi-Life</artist>
                                <album>Nihil Novi</album>
                                <mediaid>122883722</mediaid>
                                <tracklength>0</tracklength>
                                <title>Cycle</title>
                                <contentid>1</contentid>
                                <thumbnail>http://api.deezer.com/album/12864776/image</thumbnail>
                            </menuitem>
                            <menuitem type="1" available="1">
                                <artist>Bill Evans Trio</artist>
                                <album>Everybody Digs Bill Evans (Remastered)</album>
                                <mediaid>4156086</mediaid>
                                <tracklength>0</tracklength>
                                <title>What Is There To Say? (Album Version)</title>
                                <contentid>2</contentid>
                                <thumbnail>http://api.deezer.com/album/387401/image</thumbnail>
                            </menuitem>
                        </menulist>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        playlist = api.get_cp_player_playlist(0, 30)

        self.assertEqual(len(playlist), 3)
        self.assertEqual(playlist[0], {
            '@type': '1',
            '@available': '1',
            '@currentplaying': '1',
            'artist': 'Madeleine Peyroux',
            'album': 'Careless Love',
            'mediaid': '881851',
            'tracklength': '0',
            'title': 'Don\'t Wait Too Long',
            'contentid': '0',
            'thumbnail': 'http://api.deezer.com/album/100127/image',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_skip_current_track(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetSkipCurrentTrack%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <CPM>
                    <method>SkipInfo</method>
                    <version>0.1</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>407c385a-17ef-11e9-b3ee-48e244f52360</user_identifier>
                    <response result="ok">
                        <cpname>Deezer</cpname>
                        <timestamp>2019-01-14T11:21:25Z</timestamp>
                        <category isroot="1" />
                        <category_localized />
                        <skipstatus>1</skipstatus>
                        <root>Flow</root>
                        <root_index>0</root_index>
                        <root_localized>Flow</root_localized>
                    </response>
                </CPM>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_skip_current_track()

    @httpretty.activate(allow_net_connect=False)
    def test_get_current_play_time(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetCurrentPlayTime%3C/name%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>MusicPlayTime</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <timelength>168</timelength>
                        <playtime>121</playtime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        play_time = api.get_current_play_time()

        self.assertEqual(play_time, {
            'timelength': '168',
            'playtime': '121',
        })

    @httpretty.activate(allow_net_connect=False)
    def test_set_play_cp_playlist_track(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/CPM?cmd=%3Cname%3ESetPlayCpPlaylistTrack%3C/name%3E%3Cp%20type%3D%22dec%22%20name%3D%22selectitemid%22%20val%3D%220%22/%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>StopPlaybackEvent</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier>public</user_identifier>
                    <response result="ok">
                        <playtime>3</playtime>
                    </response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.set_play_cp_playlist_track(0)
