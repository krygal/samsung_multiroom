import unittest
from unittest.mock import MagicMock

from samsung_multiroom.service import REPEAT_ALL
from samsung_multiroom.service import REPEAT_OFF
from samsung_multiroom.service.tunein import TuneInPlayer


def _get_player():
    api = MagicMock()
    api.get_preset_list.return_value = [
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
    api.get_radio_info.return_value = {
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

    player = TuneInPlayer(api)

    return (player, api)


class TestTuneInPlayer(unittest.TestCase):

    def test_is_supported(self):
        player, api = _get_player()

        self.assertTrue(player.is_play_supported())
        self.assertFalse(player.is_jump_supported())
        self.assertTrue(player.is_resume_supported())
        self.assertFalse(player.is_stop_supported())
        self.assertTrue(player.is_pause_supported())
        self.assertTrue(player.is_next_supported())
        self.assertTrue(player.is_previous_supported())
        self.assertFalse(player.is_repeat_supported())
        self.assertFalse(player.is_shuffle_supported())

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

        player, api = _get_player()

        player.play(playlist)

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

        player, api = _get_player()

        self.assertFalse(player.play(playlist))

        api.set_play_select.assert_not_called()

    def test_jump(self):
        player, api = _get_player()

        player.jump(50)

        api.set_search_time.assert_not_called()

    def test_resume(self):
        player, api = _get_player()

        player.resume()

        api.set_select_radio.assert_called_once()

    @unittest.skip('Pending implementation')
    def test_stop(self):
        player, api = _get_player()

        player.stop()

    def test_pause(self):
        player, api = _get_player()

        player.pause()

        api.set_playback_control.assert_called_once_with('pause')

    @unittest.mock.patch('inspect.signature')
    def test_next(self, signature):
        signature.return_value = type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}})

        player, api = _get_player()

        player.next()

        api.get_preset_list.assert_called_once_with(start_index=0, list_count=30)
        api.get_radio_info.assert_called_once()
        api.set_play_preset.assert_called_once_with(1, 1)
        api.set_select_radio.assert_called_once()

    @unittest.mock.patch('inspect.signature')
    def test_previous(self, signature):
        signature.return_value = type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}})

        player, api = _get_player()

        player.previous()

        api.get_preset_list.assert_called_once_with(start_index=0, list_count=30)
        api.get_radio_info.assert_called_once()
        api.set_play_preset.assert_called_once_with(0, 4)
        api.set_select_radio.assert_called_once()

    def test_repeat(self):
        player, api = _get_player()

        player.repeat(REPEAT_ALL)

        api.set_repeat_mode.assert_not_called()

    def test_shuffle(self):
        player, api = _get_player()

        player.shuffle(True)

        api.set_shuffle_mode.assert_not_called()

    def test_get_repeat(self):
        player, api = _get_player()

        repeat = player.get_repeat()

        self.assertEqual(repeat, REPEAT_OFF)

        api.get_repeat_mode.assert_not_called()

    def test_get_shuffle(self):
        player, api = _get_player()

        shuffle = player.get_shuffle()

        self.assertFalse(shuffle)

        api.get_repeat_mode.assert_not_called()

    def test_get_current_track(self):
        player, api = _get_player()

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

    def test_is_active(self):
        player, api = _get_player()

        self.assertTrue(player.is_active('wifi', 'cp'))
        self.assertFalse(player.is_active('wifi', 'dlna'))
        self.assertFalse(player.is_active('bt'))
