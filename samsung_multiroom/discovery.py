"""Discover speakers on your local network."""
from .factory import speaker_factory


class SpeakerDiscovery:
    """
    Discover speakers on your local network.
    """

    def __init__(self):
        """Init."""
        self._speakers = {}

    def discover(self):
        """
        Discover speakers.

        :returns: List of Speaker instances
        """
        import upnpclient
        from urllib.parse import urlparse

        devices = upnpclient.discover()
        for device in devices:
            if not self._is_compatible_device(device):
                continue

            url = urlparse(device.location)
            hostname = url.hostname

            if hostname in self._speakers:
                continue

            self._speakers[hostname] = speaker_factory(hostname)

        return list(self._speakers.values())

    def _is_compatible_device(self, device):
        """
        Samsung speakers report on /smp_3_ and /smp_7_
        Samsung TVs report on /smp_2_ /smp_7_ /smp_15_ /smp_25_

        Therefore /smp_3_ seems to be specific to Samsung speakers.
        """
        valid_services = [s for s in device.services if s.service_id == 'urn:samsung.com:serviceId:MultiScreenService']
        valid_location = '/smp_3_' in device.location

        return valid_services and valid_location
