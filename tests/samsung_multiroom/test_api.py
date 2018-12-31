import re
import unittest

import httpretty
import requests
import xmltodict

from samsung_multiroom.api import COMMAND_CPM
from samsung_multiroom.api import COMMAND_UIC
from samsung_multiroom.api import METHOD_GET
from samsung_multiroom.api import SamsungMultiroomApi
from samsung_multiroom.api import SamsungMultiroomApiException


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

    @httpretty.activate(allow_net_connect=False)
    def test_get_main_info(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://192.168.1.129:55001/UIC?cmd=%3Cname%3EGetMainInfo%3C%2Fname%3E',
            match_querystring=True,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <UIC>
                    <method>GetMainInfo</method>
                    <version>1.0</version>
                    <speakerip>192.168.1.129</speakerip>
                    <user_identifier></user_identifier>
                    <response result="ok"></response>
                </UIC>"""
        )

        api = SamsungMultiroomApi('192.168.1.129', 55001)
        api.get_main_info()

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
                'objectid': '22$@52942',
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
