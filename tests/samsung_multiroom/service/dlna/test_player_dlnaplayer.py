import unittest
from unittest.mock import MagicMock

from samsung_multiroom.service import REPEAT_ALL
from samsung_multiroom.service import REPEAT_ONE
from samsung_multiroom.service.dlna import DlnaPlayer


def _get_player():
    api = MagicMock()

    player = DlnaPlayer(api)

    return (player, api)


class TestDlnaPlayer(unittest.TestCase):

    def test_is_supported(self):
        player, api = _get_player()

        self.assertTrue(player.is_play_supported())
        self.assertTrue(player.is_jump_supported())
        self.assertTrue(player.is_resume_supported())
        self.assertFalse(player.is_stop_supported())
        self.assertTrue(player.is_pause_supported())
        self.assertTrue(player.is_next_supported())
        self.assertTrue(player.is_previous_supported())
        self.assertTrue(player.is_repeat_supported())
        self.assertTrue(player.is_shuffle_supported())

    def test_play(self):
        playlist = [
            type('Item', (object, ), {
                'object_id': 'id1',
                'object_type': 'some_type',
                'title': 'title 1',
            }),
            type('Item', (object, ), {
                'device_udn': 'device_udn',
                'object_id': 'id2',
                'object_type': 'dlna_audio',
                'title': 'track 2',
                'artist': 'artist 2',
                'thumbnail_url': 'thumb 2'
            }),
            type('Item', (object, ), {
                'device_udn': 'device_udn',
                'object_id': 'id3',
                'object_type': 'dlna_audio',
                'title': 'track 3',
                'artist': 'artist 3',
                'thumbnail_url': 'thumb 3'
            }),
            type('Item', (object, ), {
                'object_id': 'id4',
                'object_type': 'some_type2',
                'title': 'title 4',
            })
        ]

        player, api = _get_player()

        self.assertTrue(player.play(playlist))

        items = [
            {
                'device_udn': 'device_udn',
                'object_id': 'id2',
                'title': 'track 2',
                'artist': 'artist 2',
                'thumbnail': 'thumb 2'
            },
            {
                'device_udn': 'device_udn',
                'object_id': 'id3',
                'title': 'track 3',
                'artist': 'artist 3',
                'thumbnail': 'thumb 3'
            }
        ]

        api.set_playlist_playback_control.assert_called_once_with(items)

    def test_play_returns_false_for_unsupported_playlist(self):
        playlist = [
            type('Item', (object, ), {
                'object_id': 'id1',
                'object_type': 'some_type',
                'title': 'title 1',
            }),
            type('Item', (object, ), {
                'object_id': 'id4',
                'object_type': 'some_type2',
                'title': 'title 4',
            })
        ]

        player, api = _get_player()

        self.assertFalse(player.play(playlist))

        api.set_playlist_playback_control.assert_not_called()

    def test_jump(self):
        player, api = _get_player()

        player.jump(50)

        api.set_search_time.assert_called_once_with(50)

    def test_resume(self):
        player, api = _get_player()

        player.resume()

        api.set_playback_control.assert_called_once_with('resume')

    @unittest.skip('Pending implementation')
    def test_stop(self):
        player, api = _get_player()

        player.stop()

    def test_pause(self):
        player, api = _get_player()

        player.pause()

        api.set_playback_control.assert_called_once_with('pause')

    def test_next(self):
        player, api = _get_player()

        player.next()

        api.set_trick_mode.assert_called_once_with('next')

    def test_previous(self):
        player, api = _get_player()

        player.previous()

        api.set_trick_mode.assert_called_once_with('previous')

    def test_repeat(self):
        player, api = _get_player()

        player.repeat(REPEAT_ALL)

        api.set_repeat_mode.assert_called_once_with('all')

    def test_shuffle(self):
        player, api = _get_player()

        player.shuffle(True)

        api.set_shuffle_mode.assert_called_once_with(True)

    def test_repeat_raises_value_error(self):
        player, api = _get_player()

        self.assertRaises(ValueError, player.repeat, 'unsupported_mode')

        api.set_repeat_mode.assert_not_called()

    def test_get_repeat(self):
        player, api = _get_player()
        api.get_repeat_mode.return_value = 'one'

        repeat = player.get_repeat()

        self.assertEqual(repeat, REPEAT_ONE)

        api.get_repeat_mode.assert_called_once()

    def test_get_shuffle(self):
        player, api = _get_player()
        api.get_shuffle_mode.return_value = True

        shuffle = player.get_shuffle()

        self.assertTrue(shuffle)

        api.get_shuffle_mode.assert_called_once()

    def test_get_current_track(self):
        player, api = _get_player()
        api.get_music_info.return_value = {
            'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
            'playertype': 'allshare',
            'playbacktype': 'folder',
            'sourcename': None,
            'parentid': '22$30224',
            'parentid2': None,
            'playindex': '8',
            'objectid': '22$@52947',
            'title': 'New star in the sky',
            'artist': 'Air',
            'album': 'Moon Safari',
            'thumbnail': 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52947.jpg',
            'timelength': '0:05:40.000',
            'playtime': '325067',
            'seek': 'enable',
            'pause': 'enable',
        }

        track = player.get_current_track()

        api.get_music_info.assert_called_once()

        self.assertEqual(track.title, 'New star in the sky')
        self.assertEqual(track.artist, 'Air')
        self.assertEqual(track.album, 'Moon Safari')
        self.assertEqual(track.duration, 340)
        self.assertEqual(track.position, 325)
        self.assertEqual(track.thumbnail_url, 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52947.jpg')
        self.assertEqual(track.device_udn, 'uuid:00113249-398f-0011-8f39-8f3949321100')
        self.assertEqual(track.object_id, '22$@52947')
        self.assertEqual(track.object_type, 'dlna_audio')

    def test_is_active(self):
        player, api = _get_player()

        self.assertTrue(player.is_active('wifi', 'dlna'))
        self.assertFalse(player.is_active('wifi', 'cp'))
        self.assertFalse(player.is_active('bt'))
