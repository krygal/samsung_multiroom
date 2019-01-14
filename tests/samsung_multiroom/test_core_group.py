import unittest
from unittest.mock import MagicMock

from samsung_multiroom.clock import ClockGroup
from samsung_multiroom.core import SpeakerGroup
from samsung_multiroom.equalizer import EqualizerGroup


def _get_speaker_group():
    api = MagicMock()

    speakers = [
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]

    name = 'Test group'

    speaker_group = SpeakerGroup(api, name, speakers)

    return (speaker_group, api, speakers)


class TestSpeakerGroup(unittest.TestCase):

    def test_ip_address(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].ip_address = '192.168.1.129'

        ip_address = speaker_group.ip_address

        self.assertEqual(ip_address, '192.168.1.129')

    def test_mac_address(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].mac_address = '00:11:22:33:44:55'

        mac_address = speaker_group.mac_address

        self.assertEqual(mac_address, '00:11:22:33:44:55')

    def test_get_name(self):
        speaker_group, api, speakers = _get_speaker_group()

        name = speaker_group.get_name()

        self.assertEqual(name, 'Test group')

    def test_set_name(self):
        speaker_group, api, speakers = _get_speaker_group()

        speaker_group.set_name('Updated group name')
        name = speaker_group.get_name()

        self.assertEqual(name, 'Updated group name')

    def test_get_volume_returns_main_speaker_volume(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].get_volume.return_value = 13

        volume = speaker_group.get_volume()

        self.assertEqual(volume, 13)
        speakers[0].get_volume.assert_called_once()
        speakers[1].get_volume.assert_not_called()
        speakers[2].get_volume.assert_not_called()

    def test_set_volume_updates_proportionally(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].get_volume.return_value = 20
        speakers[1].get_volume.return_value = 10
        speakers[2].get_volume.return_value = 5

        speaker_group.set_volume(40)

        speakers[0].set_volume.assert_called_once_with(40)
        speakers[1].set_volume.assert_called_once_with(20)
        speakers[2].set_volume.assert_called_once_with(10)

    def test_set_volume_stays_within_bounds(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].get_volume.return_value = 20
        speakers[1].get_volume.return_value = 60
        speakers[2].get_volume.return_value = 60

        speaker_group.set_volume(40)

        speakers[0].set_volume.assert_called_once_with(40)
        speakers[1].set_volume.assert_called_once_with(100)
        speakers[2].set_volume.assert_called_once_with(100)

    def test_get_sources(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].get_sources.return_value = ['aux', 'bt', 'hdmi', 'optical', 'soundshare', 'wifi']

        sources = speaker_group.get_sources()

        self.assertEqual(sorted(sources), sorted(['aux', 'bt', 'hdmi', 'optical', 'soundshare', 'wifi']))

        speakers[0].get_sources.assert_called_once()
        speakers[1].get_sources.assert_not_called()
        speakers[2].get_sources.assert_not_called()

    def test_get_source(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].get_source.return_value = 'wifi'

        source = speaker_group.get_source()

        self.assertEqual(source, 'wifi')

        speakers[0].get_source.assert_called_once()
        speakers[1].get_source.assert_not_called()
        speakers[2].get_source.assert_not_called()

    def test_set_source(self):
        speaker_group, api, speakers = _get_speaker_group()

        speaker_group.set_source('hdmi')

        speakers[0].set_source.assert_called_once_with('hdmi')
        speakers[1].set_source.assert_not_called()
        speakers[2].set_source.assert_not_called()

    def test_is_muted_returns_true_if_all_muted(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].is_muted.return_value = True
        speakers[1].is_muted.return_value = True
        speakers[2].is_muted.return_value = True

        muted = speaker_group.is_muted()

        self.assertTrue(muted)

        speakers[0].is_muted.assert_called_once()
        speakers[1].is_muted.assert_called_once()
        speakers[2].is_muted.assert_called_once()

    def test_is_muted_returns_false_if_one_unmuted(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].is_muted.return_value = True
        speakers[1].is_muted.return_value = False
        speakers[2].is_muted.return_value = True

        muted = speaker_group.is_muted()

        self.assertFalse(muted)

        speakers[0].is_muted.assert_called_once()
        speakers[1].is_muted.assert_called_once()
        speakers[2].is_muted.assert_not_called()

    def test_mute_mutes_all_speakers(self):
        speaker_group, api, speakers = _get_speaker_group()

        speaker_group.mute()

        speakers[0].mute.assert_called_once()
        speakers[1].mute.assert_called_once()
        speakers[2].mute.assert_called_once()

    def test_unmute_unmutes_all_speakers(self):
        speaker_group, api, speakers = _get_speaker_group()

        speaker_group.unmute()

        speakers[0].unmute.assert_called_once()
        speakers[1].unmute.assert_called_once()
        speakers[2].unmute.assert_called_once()

    def test_get_services_names_returns_main_speaker_services(self):
        speaker_group, api, speakers = _get_speaker_group()

        speaker_group.get_services_names()

        speakers[0].get_services_names.assert_called_once()
        speakers[1].get_services_names.assert_not_called()
        speakers[2].get_services_names.assert_not_called()

    def test_service_returns_main_speaker_service(self):
        speaker_group, api, speakers = _get_speaker_group()

        speaker_group.service('dlna')

        speakers[0].service.assert_called_once_with('dlna')
        speakers[1].service.assert_not_called()
        speakers[2].service.assert_not_called()

    def test_player_returns_main_speaker_player(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].player = MagicMock()

        player = speaker_group.player

        self.assertEqual(player, speakers[0].player)

    def test_browser_returns_main_speaker_browser(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].browser.return_value = MagicMock()

        browser = speaker_group.browser('b2')

        self.assertEqual(browser, speakers[0].browser.return_value)

        speakers[0].browser.assert_called_once_with('b2')

    def test_equalizer(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].equalizer = MagicMock()
        speakers[1].equalizer = MagicMock()
        speakers[2].equalizer = MagicMock()

        equalizer = speaker_group.equalizer

        self.assertIsInstance(equalizer, EqualizerGroup)
        self.assertEqual(equalizer.equalizers, [speakers[0].equalizer, speakers[1].equalizer, speakers[2].equalizer])

    def test_clock(self):
        speaker_group, api, speakers = _get_speaker_group()
        speakers[0].clock = MagicMock()
        speakers[1].clock = MagicMock()
        speakers[2].clock = MagicMock()

        clock = speaker_group.clock

        self.assertIsInstance(clock, ClockGroup)
        self.assertEqual(clock.clocks, [speakers[0].clock, speakers[1].clock, speakers[2].clock])

    def test_group_adds_speakers_to_existing_group(self):
        speaker_group, api, speakers = _get_speaker_group()

        new_speakers = [
            MagicMock(),
            MagicMock(),
        ]

        speakers[0].group.return_value = MagicMock()
        speakers[0].group.return_value.get_name.return_value = 'Expanded group'
        speakers[0].group.return_value.speakers = speakers + new_speakers

        new_speaker_group = speaker_group.group('Expanded group', new_speakers)

        self.assertEqual(new_speaker_group, speaker_group)
        self.assertEqual(new_speaker_group.get_name(), 'Expanded group')
        self.assertEqual(new_speaker_group.speakers, speakers + new_speakers)

        speakers[0].group.assert_called_once_with('Expanded group', speakers[1:] + new_speakers)

    def test_ungroup_ungroups_all_speakers(self):
        speaker_group, api, speakers = _get_speaker_group()

        speaker_group.ungroup()

        speakers[0].ungroup.assert_called_once()
        speakers[1].ungroup.assert_called_once()
        speakers[2].ungroup.assert_called_once()
