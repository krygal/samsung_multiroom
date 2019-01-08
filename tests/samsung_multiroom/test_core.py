import unittest
from unittest.mock import MagicMock

from samsung_multiroom import SamsungMultiroomSpeaker
from samsung_multiroom.core import Speaker


def get_speaker():
    api = MagicMock()

    clock = MagicMock()
    equalizer = MagicMock()
    player_operator = MagicMock()
    browsers = [
        MagicMock(),
        MagicMock(),
    ]

    browsers[0].get_name.return_value = 'b1'
    browsers[1].get_name.return_value = 'b2'

    speaker = Speaker(api, clock, equalizer, player_operator, browsers)

    return (speaker, api, clock, equalizer, player_operator, browsers)


class TestSpeaker(unittest.TestCase):

    def test_factory(self):
        self.assertIsInstance(SamsungMultiroomSpeaker('192.168.1.111'), Speaker)

    def test_get_name(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()
        api.get_speaker_name.return_value = 'Speaker name'

        name = speaker.get_name()

        api.get_speaker_name.assert_called_once()
        self.assertEqual(name, 'Speaker name')

    def test_set_name(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        speaker.set_name('Living Room')

        api.set_speaker_name.assert_called_once_with('Living Room')

    def test_get_volume(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()
        api.get_volume.return_value = 10

        volume = speaker.get_volume()

        api.get_volume.assert_called_once()
        self.assertEqual(volume, 10)

    def test_set_volume(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        speaker.set_volume(10)

        api.set_volume.assert_called_once_with(10)

    def test_get_sources(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        sources = speaker.get_sources()

        self.assertEqual(sorted(sources), sorted(['aux', 'bt', 'hdmi', 'optical', 'soundshare', 'wifi']))

    def test_get_source(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()
        api.get_func.return_value = {'function':'wifi', 'submode':'dlna'}

        source = speaker.get_source()

        api.get_func.assert_called_once()
        self.assertEqual(source, 'wifi')

    def test_set_source(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        speaker.set_source('hdmi')

        api.set_func.assert_called_once_with('hdmi')

    def test_is_muted(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()
        api.get_mute.return_value = True

        muted = speaker.is_muted()

        api.get_mute.assert_called_once()
        self.assertTrue(muted)

    def test_mute(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        speaker.mute()

        api.set_mute.assert_called_once_with(True)

    def test_unmute(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        speaker.unmute()

        api.set_mute.assert_called_once_with(False)

    def test_get_player(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        player = speaker.get_player()

        self.assertEqual(player, player_operator)

    def test_get_browser(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        browser = speaker.get_browser('b2')

        self.assertEqual(browser, browsers[1])

    def test_get_equalizer(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        eq = speaker.get_equalizer()

        self.assertEqual(eq, equalizer)

    def test_get_clock(self):
        speaker, api, clock, equalizer, player_operator, browsers = get_speaker()

        cl = speaker.get_clock()

        self.assertEqual(cl, clock)
