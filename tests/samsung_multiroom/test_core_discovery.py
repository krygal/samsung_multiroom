import unittest
from unittest.mock import MagicMock

from samsung_multiroom import SamsungSpeakerDiscovery


class TestSpeakerDiscovery(unittest.TestCase):

    @unittest.mock.patch('upnpclient.discover')
    def test_discover(self, upnpclient):
        upnp_devices = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        upnpclient.return_value = upnp_devices

        upnp_devices[0].location = 'http://192.168.1.129:7676/smp_3_'
        upnp_devices[1].location = 'http://192.168.1.165:7676/smp_3_'
        upnp_devices[2].location = 'http://192.168.1.216:7676/smp_3_'
        upnp_devices[3].location = 'http://192.168.1.60:7676/smp_7_'

        upnp_devices[0].services = [MagicMock(service_id='urn:samsung.com:serviceId:MultiScreenService')]
        upnp_devices[1].services = [MagicMock(service_id='invalid service')]
        upnp_devices[2].services = [MagicMock(service_id='urn:samsung.com:serviceId:MultiScreenService')]
        upnp_devices[3].services = [MagicMock(service_id='urn:samsung.com:serviceId:MultiScreenService')]

        speaker_discovery = SamsungSpeakerDiscovery()
        speakers = speaker_discovery.discover()

        self.assertEqual(len(speakers), 2)
        self.assertEqual(speakers[0].ip_address, '192.168.1.129')
        self.assertEqual(speakers[1].ip_address, '192.168.1.216')
