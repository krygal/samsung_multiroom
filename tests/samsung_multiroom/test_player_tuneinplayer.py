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

    def test_play(self):
        playlist = [
            type('Item', (object, ), {
                'object_id': '1',
                'object_type': 'some_type',
                'title': 'title 1',
            }),
            type('Item', (object, ), {
                'object_id': '2',
                'object_type': 'tunein_radio',
                'title': 'radio 2',
            }),
            type('Item', (object, ), {
                'object_id': '3',
                'object_type': 'tunein_radio',
                'title': 'radio 3',
            }),
            type('Item', (object, ), {
                'object_id': '4',
                'object_type': 'some_type2',
                'title': 'title 4',
            })
        ]

        api = MagicMock()

        player = TuneInPlayer(api)
        self.assertTrue(player.play(playlist))

        api.set_play_select.assert_called_once_with('2')

    def test_play_returns_false_for_unsupported_playlist(self):
        playlist = [
            type('Item', (object, ), {
                'object_id': '1',
                'object_type': 'some_type',
                'title': 'title 1',
            }),
            type('Item', (object, ), {
                'object_id': '4',
                'object_type': 'some_type2',
                'title': 'title 4',
            })
        ]

        api = MagicMock()

        player = TuneInPlayer(api)
        self.assertFalse(player.play(playlist))

        api.set_play_select.assert_not_called()

    def test_jump(self):
        api = MagicMock()

        player = TuneInPlayer(api)
        player.jump(50)

        api.set_search_time.assert_not_called()

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

    @unittest.mock.patch('inspect.signature')
    def test_next(self, signature):
        signature.return_value = type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}})

        api = MagicMock()
        api.get_preset_list.return_value = get_preset_list_return_value()
        api.get_radio_info.return_value = get_radio_info_return_value()

        player = TuneInPlayer(api)
        player.next()

        api.get_preset_list.assert_called_once_with(start_index=0, list_count=30)
        api.get_radio_info.assert_called_once()
        api.set_play_preset.assert_called_once_with(1, 1)
        api.set_select_radio.assert_called_once()

    @unittest.mock.patch('inspect.signature')
    def test_previous(self, signature):
        signature.return_value = type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}})

        api = MagicMock()
        api.get_preset_list.return_value = get_preset_list_return_value()
        api.get_radio_info.return_value = get_radio_info_return_value()

        player = TuneInPlayer(api)
        player.previous()

        api.get_preset_list.assert_called_once_with(start_index=0, list_count=30)
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
        self.assertEqual(track.object_id, None)
        self.assertEqual(track.object_type, 'tunein_radio')

    def test_is_supported(self):
        api = MagicMock()

        player = TuneInPlayer(api)

        self.assertTrue(player.is_supported('wifi', 'cp'))
        self.assertFalse(player.is_supported('wifi', 'dlna'))
        self.assertFalse(player.is_supported('bt'))
