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
