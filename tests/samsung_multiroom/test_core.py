import unittest
from unittest.mock import MagicMock

from samsung_multiroom import SamsungMultiroomSpeaker
from samsung_multiroom.core import Speaker


class TestSpeaker(unittest.TestCase):

    def test_factory(self):
        self.assertIsInstance(SamsungMultiroomSpeaker('192.168.1.111'), Speaker)

    def test_get_name(self):
        api = MagicMock()
        api.get_speaker_name.return_value = 'Speaker name'

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        name = speaker.get_name()

        api.get_speaker_name.assert_called_once()
        self.assertEqual(name, 'Speaker name')

    def test_set_name(self):
        api = MagicMock()

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        speaker.set_name('Living Room')

        api.set_speaker_name.assert_called_once_with('Living Room')

    def test_get_volume(self):
        api = MagicMock()
        api.get_volume.return_value = 10

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        volume = speaker.get_volume()

        api.get_volume.assert_called_once()
        self.assertEqual(volume, 10)

    def test_set_volume(self):
        api = MagicMock()

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        speaker.set_volume(10)

        api.set_volume.assert_called_once_with(10)

    def test_get_sources(self):
        api = MagicMock()

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        sources = speaker.get_sources()

        self.assertEqual(sorted(sources), sorted(['aux', 'bt', 'hdmi', 'optical', 'soundshare', 'wifi']))

    def test_get_source(self):
        api = MagicMock()
        api.get_func.return_value = {'function':'wifi', 'submode':'dlna'}

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        source = speaker.get_source()

        api.get_func.assert_called_once()
        self.assertEqual(source, 'wifi')

    def test_set_source(self):
        api = MagicMock()

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        speaker.set_source('hdmi')

        api.set_func.assert_called_once_with('hdmi')

    def test_is_muted(self):
        api = MagicMock()
        api.get_mute.return_value = True

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        muted = speaker.is_muted()

        api.get_mute.assert_called_once()
        self.assertTrue(muted)

    def test_mute(self):
        api = MagicMock()

        speaker_operator = MagicMock()

        speaker = Speaker(api, speaker_operator)
        speaker.mute()

        api.set_mute.assert_called_once_with(True)

    def test_unmute(self):
        api = MagicMock()

        player_operator = MagicMock()

        speaker = Speaker(api, player_operator)
        speaker.unmute()

        api.set_mute.assert_called_once_with(False)

    def test_get_player(self):
        api = MagicMock()

        player1 = MagicMock(name='player')

        player_operator = MagicMock()
        player_operator.get_player.return_value = player1

        speaker = Speaker(api, player_operator)
        player = speaker.get_player()

        self.assertEqual(player, player1)

    def test_get_browser(self):
        api = MagicMock()

        player_operator = MagicMock()
        browsers = [
            MagicMock(),
            MagicMock(),
        ]
        browsers[0].get_name.return_value = 'b1'
        browsers[1].get_name.return_value = 'b2'

        speaker = Speaker(api, player_operator, browsers)
        browser = speaker.get_browser('b2')

        self.assertEqual(browser, browsers[1])
