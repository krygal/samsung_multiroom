import unittest
from unittest.mock import MagicMock

from samsung_multiroom.player import DlnaPlayer


class TestDlnaPlayer(unittest.TestCase):

    def test_resume(self):
        api = MagicMock()

        player = DlnaPlayer(api)
        player.resume()

        api.set_playback_control.assert_called_once_with('resume')

    @unittest.skip('Pending implementation')
    def test_stop(self):
        api = MagicMock()

        player = DlnaPlayer(api)
        player.stop()

    def test_pause(self):
        api = MagicMock()

        player = DlnaPlayer(api)
        player.pause()

        api.set_playback_control.assert_called_once_with('pause')

    def test_next(self):
        api = MagicMock()

        player = DlnaPlayer(api)
        player.next()

        api.set_trick_mode.assert_called_once_with('next')

    def test_previous(self):
        api = MagicMock()

        player = DlnaPlayer(api)
        player.previous()

        api.set_trick_mode.assert_called_once_with('previous')

    def test_get_current_track(self):
        api = MagicMock()
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

        player = DlnaPlayer(api)
        track = player.get_current_track()

        api.get_music_info.assert_called_once()

        self.assertEqual(track.title, 'New star in the sky')
        self.assertEqual(track.artist, 'Air')
        self.assertEqual(track.album, 'Moon Safari')
        self.assertEqual(track.duration, 340)
        self.assertEqual(track.position, 325)
        self.assertEqual(track.thumbnail_url, 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52947.jpg')

    def test_is_supported(self):
        api = MagicMock()

        player = DlnaPlayer(api)

        self.assertTrue(player.is_supported('wifi', 'dlna'))
        self.assertFalse(player.is_supported('wifi', 'cp'))
        self.assertFalse(player.is_supported('bt'))
