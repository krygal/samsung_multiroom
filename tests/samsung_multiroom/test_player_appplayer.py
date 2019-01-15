import unittest
from unittest.mock import MagicMock

from samsung_multiroom.player import AppPlayer


def _get_player():
    api = MagicMock()

    player = AppPlayer(api)

    return (player, api)


class TestAppPlayer(unittest.TestCase):

    def test_play(self):
        player, api = _get_player()

        playlist = [
            type('Item', (object, ), {
                'object_id': 'id1',
                'object_type': 'some_type',
                'title': 'title 1',
            }),
            type('Item', (object, ), {
                'device_udn': 'device_udn',
                'object_id': '2',
                'object_type': 'app_audio',
                'title': 'track 2',
                'artist': 'artist 2',
                'thumbnail_url': 'thumb 2'
            }),
            type('Item', (object, ), {
                'device_udn': 'device_udn',
                'object_id': '3',
                'object_type': 'app_audio',
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

        player.play(playlist)

        api.set_play_select.assert_called_once_with(['2', '3'])

    @unittest.skip('No access to app supporting this feature')
    def test_jump(self):
        pass

    def test_resume(self):
        player, api = _get_player()

        player.resume()

        api.set_playback_control.assert_called_once_with('play')

    @unittest.skip('No access to app supporting this feature')
    def test_stop(self):
        pass

    def test_pause(self):
        player, api = _get_player()

        player.pause()

        api.set_playback_control.assert_called_once_with('pause')

    def test_next(self):
        player, api = _get_player()

        player.next()

        api.set_skip_current_track.assert_called_once()

    def test_previous(self):
        player, api = _get_player()

        api.get_cp_player_playlist.return_value = [
            # we don't care about other attributes
            {
                'contentid': '0',
            },
            {
                'contentid': '1',
            },
            {
                '@currentplaying': '1',
                'contentid': '2',
            },
            {
                'contentid': '3',
            }
        ]

        player.previous()

        api.set_play_cp_playlist_track.assert_called_once_with('1')

    def test_get_current_track(self):
        player, api = _get_player()

        api.get_cp_player_playlist.return_value = [
            {
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
            },
            {
                '@type': '1',
                '@available': '1',
                'artist': 'artist',
                'album': 'album',
                'mediaid': 'mediaid',
                'tracklength': '0',
                'title': 'title',
                'contentid': '1',
                'thumbnail': 'http://thumb.url/image',
            },
            {
                '@type': '1',
                '@available': '1',
                'artist': 'artist',
                'album': 'album',
                'mediaid': 'mediaid',
                'tracklength': '0',
                'title': 'title',
                'contentid': '2',
                'thumbnail': 'http://thumb.url/image',
            }
        ]

        api.get_current_play_time.return_value = {
            'timelength': '192',
            'playtime': '35',
        }

        track = player.get_current_track()

        self.assertEqual(track.title, 'Don\'t Wait Too Long')
        self.assertEqual(track.artist, 'Madeleine Peyroux')
        self.assertEqual(track.album, 'Careless Love')
        self.assertEqual(track.duration, 192)
        self.assertEqual(track.position, 35)
        self.assertEqual(track.thumbnail_url, 'http://api.deezer.com/album/100127/image')
        self.assertEqual(track.object_id, '881851')
        self.assertEqual(track.object_type, 'app_audio')

    def test_is_supported(self):
        player, api = _get_player()

        self.assertTrue(player.is_supported('wifi', 'cp'))
        self.assertFalse(player.is_supported('wifi', 'dlna'))
        self.assertFalse(player.is_supported('bt'))
