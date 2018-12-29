import unittest
from unittest.mock import MagicMock

from samsung_multiroom.player import TuneInPlayer


def get_preset_list_return_value():
    return [
        {
            'kind': 'speaker',
            'title': 'Radio 1',
            'description': 'Radio 1 description',
            'thumbnail': 'http://radio1.org/thumbnail.png',
            'contentid': '0',
            'mediaid': '1111',
        },
        {
            'kind': 'speaker',
            'title': 'Radio 2',
            'description': 'Radio 2 description',
            'thumbnail': 'http://radio2.org/thumbnail.png',
            'contentid': '1',
            'mediaid': '2222',
        },
        {
            'kind': 'speaker',
            'title': 'Radio 3',
            'description': 'Radio 3 description',
            'thumbnail': 'http://radio3.org/thumbnail.png',
            'contentid': '2',
            'mediaid': '3333',
        },
        {
            'kind': 'my',
            'title': 'Radio 4',
            'description': 'Radio 4 description',
            'thumbnail': 'http://radio4.org/thumbnail.png',
            'contentid': '3',
            'mediaid': '4444',
        },
        {
            'kind': 'my',
            'title': 'Radio 5',
            'description': 'Radio 5 description',
            'thumbnail': 'http://radio5.org/thumbnail.png',
            'contentid': '4',
            'mediaid': '5555',
        },
    ]


def get_radio_info_return_value():
    return {
        'cpname': 'TuneIn',
        'root': 'Favorites',
        'presetindex': '0',
        'title': 'Radio 1',
        'description': 'Radio 1 description',
        'thumbnail': 'http://radio1.org/thumbnail.png',
        'mediaid': '1111',
        'allowfeedback': '0',
        'timestamp': '2018-12-28T18:07:07Z',
        'no_queue': '1',
        'playstatus': 'play',
    }


class TestTuneInPlayer(unittest.TestCase):

    def test_resume(self):
        api = MagicMock()

        player = TuneInPlayer(api)
        player.resume()

        api.set_select_radio.assert_called_once()

    @unittest.skip('Pending implementation')
    def test_stop(self):
        api = MagicMock()

        player = TuneInPlayer(api)
        player.stop()

    def test_pause(self):
        api = MagicMock()

        player = TuneInPlayer(api)
        player.pause()

        api.set_playback_control.assert_called_once_with('pause')

    def test_next(self):
        api = MagicMock()
        api.get_preset_list.return_value = get_preset_list_return_value()
        api.get_radio_info.return_value = get_radio_info_return_value()

        player = TuneInPlayer(api)
        player.next()

        api.get_preset_list.assert_called_once_with(0, 10)
        api.get_radio_info.assert_called_once()
        api.set_play_preset.assert_called_once_with(1, 1)
        api.set_select_radio.assert_called_once()

    def test_previous(self):
        api = MagicMock()
        api.get_preset_list.return_value = get_preset_list_return_value()
        api.get_radio_info.return_value = get_radio_info_return_value()

        player = TuneInPlayer(api)
        player.previous()

        api.get_preset_list.assert_called_once_with(0, 10)
        api.get_radio_info.assert_called_once()
        api.set_play_preset.assert_called_once_with(0, 4)
        api.set_select_radio.assert_called_once()

    def test_get_current_track(self):
        api = MagicMock()
        api.get_radio_info.return_value = get_radio_info_return_value()

        player = TuneInPlayer(api)
        track = player.get_current_track()

        api.get_radio_info.assert_called_once()

        self.assertEqual(track.title, 'Radio 1 description')
        self.assertEqual(track.artist, 'Radio 1')
        self.assertEqual(track.album, None)
        self.assertEqual(track.duration, None)
        self.assertEqual(track.position, None)
        self.assertEqual(track.thumbnail_url, 'http://radio1.org/thumbnail.png')

    def test_is_supported(self):
        api = MagicMock()

        player = TuneInPlayer(api)

        self.assertTrue(player.is_supported('wifi', 'cp'))
        self.assertFalse(player.is_supported('wifi', 'dlna'))
        self.assertFalse(player.is_supported('bt'))
