import unittest
from unittest.mock import MagicMock

from samsung_multiroom import SamsungMultiroomSpeaker
from samsung_multiroom.core import Speaker
from samsung_multiroom.core import SpeakerGroup


def get_speaker():
    api = MagicMock()
    api.ip_address = '192.168.1.129'

    clock = MagicMock()
    equalizer = MagicMock()
    player_operator = MagicMock()

    service_registry = MagicMock()

    speaker = Speaker(api, clock, equalizer, player_operator, service_registry)

    return (speaker, api, clock, equalizer, player_operator, service_registry)


class TestSpeaker(unittest.TestCase):

    def test_factory(self):
        self.assertIsInstance(SamsungMultiroomSpeaker('192.168.1.129'), Speaker)

    def test_get_name(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()
        api.get_speaker_name.return_value = 'Speaker name'

        name = speaker.get_name()

        api.get_speaker_name.assert_called_once()
        self.assertEqual(name, 'Speaker name')

    def test_set_name(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        speaker.set_name('Living Room')

        api.set_speaker_name.assert_called_once_with('Living Room')

    def test_get_volume(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()
        api.get_volume.return_value = 10

        volume = speaker.get_volume()

        api.get_volume.assert_called_once()
        self.assertEqual(volume, 10)

    def test_set_volume(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        speaker.set_volume(10)

        api.set_volume.assert_called_once_with(10)

    def test_get_sources(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        sources = speaker.get_sources()

        self.assertEqual(sorted(sources), sorted(['aux', 'bt', 'hdmi', 'optical', 'soundshare', 'wifi']))

    def test_get_source(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()
        api.get_func.return_value = {'function':'wifi', 'submode':'dlna'}

        source = speaker.get_source()

        api.get_func.assert_called_once()
        self.assertEqual(source, 'wifi')

    def test_set_source(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        speaker.set_source('hdmi')

        api.set_func.assert_called_once_with('hdmi')

    def test_is_muted(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()
        api.get_mute.return_value = True

        muted = speaker.is_muted()

        api.get_mute.assert_called_once()
        self.assertTrue(muted)

    def test_mute(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        speaker.mute()

        api.set_mute.assert_called_once_with(True)

    def test_unmute(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        speaker.unmute()

        api.set_mute.assert_called_once_with(False)

    def test_get_services_names(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()
        service_registry.get_services_names.return_value = ['dlna', 'tunein', 'deezer', 'spotify']

        services_names = speaker.get_services_names()

        self.assertEqual(services_names, ['dlna', 'tunein', 'deezer', 'spotify'])
        service_registry.get_services_names.assert_called_once()

    def test_service(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()
        service_registry.service.return_value = MagicMock()

        service = speaker.service('dlna')

        self.assertEqual(service, service_registry.service.return_value)
        service_registry.service.assert_called_once_with('dlna')

    def test_player(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        player = speaker.player

        self.assertEqual(player, player_operator)

    def test_browser(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        browser = MagicMock()
        service_registry.service.return_value = MagicMock(browser=browser)

        service_browser = speaker.browser('b2')

        self.assertEqual(service_browser, browser)
        service_registry.service.assert_called_once_with('b2')

    def test_equalizer(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        eq = speaker.equalizer

        self.assertEqual(eq, equalizer)

    def test_clock(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        cl = speaker.clock

        self.assertEqual(cl, clock)

    def test_group(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        speaker1 = MagicMock()
        speaker2 = MagicMock()

        api.get_speaker_name.return_value = 'This speaker'
        api.get_main_info.return_value = {
            'spkmacaddr': '00:00:00:00:00:00'
        }

        speaker1.get_name.return_value = 'Speaker 1'
        speaker2.get_name.return_value = 'Speaker 2'

        speaker1.ip_address = '192.168.1.165'
        speaker2.ip_address = '192.168.1.216'

        speaker1.mac_address = '11:11:11:11:11:11'
        speaker2.mac_address = '22:22:22:22:22:22'

        group = speaker.group('My group', [speaker1, speaker2])

        self.assertIsInstance(group, SpeakerGroup)
        api.set_multispk_group.assert_called_once_with('My group', [
            {
                'name': 'This speaker',
                'ip': '192.168.1.129',
                'mac': '00:00:00:00:00:00',
            },
            {
                'name': 'Speaker 1',
                'ip': '192.168.1.165',
                'mac': '11:11:11:11:11:11',
            },
            {
                'name': 'Speaker 2',
                'ip': '192.168.1.216',
                'mac': '22:22:22:22:22:22',
            }
        ])

    def test_ungroup(self):
        speaker, api, clock, equalizer, player_operator, service_registry = get_speaker()

        speaker.ungroup()

        api.set_ungroup.assert_called_once()
