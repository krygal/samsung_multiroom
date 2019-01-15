"""Entry control for speaker operation. """
import abc

from .api import SamsungMultiroomApi
from .clock import Alarm
from .clock import Clock
from .clock import ClockGroup
from .clock import Timer
from .equalizer import Equalizer
from .equalizer import EqualizerGroup
from .player import AppPlayer
from .player import DlnaPlayer
from .player import PlayerOperator
from .player import TuneInPlayer
from .service import ServiceRegistry


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


class SpeakerBase(metaclass=abc.ABCMeta):
    """Speaker interface to control speaker operation."""

    @property
    def ip_address(self):
        """
        :returns: Speaker's ip address
        """
        raise NotImplementedError()

    @property
    def mac_address(self):
        """
        :returns: Speaker's mac address
        """
        raise NotImplementedError()

    def get_name(self):
        """
        Retrieve speaker's name.

        :returns: Speaker name string
        """
        raise NotImplementedError()

    def set_name(self, name):
        """
        Set speaker's name.

        :param name: Speaker name string
        """
        raise NotImplementedError()

    def get_volume(self):
        """
        Get current speaker volume.

        :returns: int current volume
        """
        raise NotImplementedError()

    def set_volume(self, volume):
        """
        Set speaker volume.

        :param volume: speaker volume, integer between 0 and 100
        """
        raise NotImplementedError()

    def get_sources(self):
        """
        Get all supported sources.

        :returns: List of supported sources.
        """
        raise NotImplementedError()

    def get_source(self):
        """
        Get currently selected source.

        :returns: selected source string.
        """
        raise NotImplementedError()

    def set_source(self, source):
        """
        Set speaker source.

        :param source: Speaker source, one of returned by get_sources()
        """
        raise NotImplementedError()

    def is_muted(self):
        """
        Check if speaker is muted.

        :returns: True if muted, False otherwise
        """
        raise NotImplementedError()

    def mute(self):
        """Mute the speaker."""
        raise NotImplementedError()

    def unmute(self):
        """Unmute the speaker."""
        raise NotImplementedError()

    def get_services_names(self):
        """
        Get all supported services names.

        :returns: List of strings
        """
        raise NotImplementedError()

    def service(self, name):
        """
        Get service by type

        :returns: Service instance
        """
        raise NotImplementedError()

    @property
    def clock(self):
        """
        Get clock to control time functions.

        :returns: Clock instance
        """
        raise NotImplementedError()

    @property
    def equalizer(self):
        """
        Get equalizer to control sound adjustments.

        :returns: Equalizer instance
        """
        raise NotImplementedError()

    @property
    def player(self):
        """
        Get currently active player.

        Use player to control playback e.g. pause, resume, get track info etc.

        :returns: Player instance
        """
        raise NotImplementedError()

    def browser(self, name):
        """
        Get media browser by type

        :returns: Browser instance
        """
        raise NotImplementedError()

    def group(self, name, speakers):
        """
        Group this speaker with another ones.

        This speaker will be the main speaker controlling the playback.

        :param speaker: List of Speaker instances
        :returns: SpeakerGroup instance
        """
        raise NotImplementedError()

    def ungroup(self):
        """
        Remove this speaker from its current group.
        """
        raise NotImplementedError()


class Speaker(SpeakerBase):
    """Entry control for speaker operation."""

    def __init__(self, api, clock, equalizer, player_operator, service_registry):
        """
        Initialise the speaker.

        :param api: SamsungMultiroomApi instance
        :param clock: Clock instance
        :param equalizer: Equalizer instance
        :param player_operator: PlayerOperator instance
        :param service_registry: ServiceRegistry instance
        """
        self._api = api
        self._clock = clock
        self._equalizer = equalizer
        self._player_operator = player_operator
        self._service_registry = service_registry

    @property
    def ip_address(self):
        """
        :returns: Speaker's ip address
        """
        return self._api.ip_address

    @property
    def mac_address(self):
        """
        :returns: Speaker's mac address
        """
        main_info = self._api.get_main_info()
        return main_info['spkmacaddr']

    def get_name(self):
        """
        Retrieve speaker's name.

        :returns: Speaker name string
        """
        return self._api.get_speaker_name()

    def set_name(self, name):
        """
        Set speaker's name.

        :param name: Speaker name string
        """
        self._api.set_speaker_name(name)

    def get_volume(self):
        """
        Get current speaker volume.

        :returns: int current volume
        """
        return self._api.get_volume()

    def set_volume(self, volume):
        """
        Set speaker volume.

        :param volume: speaker volume, integer between 0 and 100
        """
        if not isinstance(volume, int) or int(volume) < 0 or int(volume) > 100:
            raise ValueError('Volume must be integer between 0 and 100')

        self._api.set_volume(volume)

    def get_sources(self):
        """
        Get all supported sources.

        :returns: List of supported sources.
        """
        return ['aux', 'bt', 'hdmi', 'optical', 'soundshare', 'wifi']

    def get_source(self):
        """
        Get currently selected source.

        :returns: selected source string.
        """
        function = self._api.get_func()
        return function['function']

    def set_source(self, source):
        """
        Set speaker source.

        :param source: Speaker source, one of returned by get_sources()
        """
        if source not in self.get_sources():
            raise ValueError('Invalid source {0}'.format(source))

        self._api.set_func(source)

    def is_muted(self):
        """
        Check if speaker is muted.

        :returns: True if muted, False otherwise
        """
        return self._api.get_mute()

    def mute(self):
        """Mute the speaker."""
        self._api.set_mute(True)

    def unmute(self):
        """Unmute the speaker."""
        self._api.set_mute(False)

    def get_services_names(self):
        """
        Get all supported services names.

        :returns: List of strings
        """
        return self._service_registry.get_services_names()

    def service(self, name):
        """
        Get service by type

        :returns: Service instance
        """
        return self._service_registry.service(name)

    @property
    def clock(self):
        """
        Get clock to control time functions.

        :returns: Clock instance
        """
        return self._clock

    @property
    def equalizer(self):
        """
        Get equalizer to control sound adjustments.

        :returns: Equalizer instance
        """
        return self._equalizer

    @property
    def player(self):
        """
        Get currently active player.

        Use player to control playback e.g. pause, resume, get track info etc.

        :returns: Player instance
        """
        return self._player_operator

    def browser(self, name):
        """
        Get media browser by type

        :returns: Browser instance
        """
        return self._service_registry.service(name).browser

    def group(self, name, speakers):
        """
        Group this speaker with another ones.

        This speaker will be the main speaker controlling the playback.

        :param speaker: List of Speaker instances
        :returns: SpeakerGroup instance
        """
        if isinstance(speakers, Speaker):
            speakers = [speakers]

        speakers = [self] + speakers

        speakers_info = []
        for speaker in speakers:
            speakers_info.append({
                'name': speaker.get_name(),
                'ip': speaker.ip_address,
                'mac': speaker.mac_address,
            })

        if not name:
            name = ' + '.join([s['name'] for s in speakers_info])

        self._api.set_multispk_group(name, speakers_info)

        return SpeakerGroup(self._api, name, speakers)

    def ungroup(self):
        """
        Remove this speaker from its current group.
        """
        self._api.set_ungroup()


class SpeakerGroup(SpeakerBase):
    """
    Speaker group.

    Use Speaker.group() to initiate grouping.
    """

    def __init__(self, api, name, speakers):
        """
        The first speaker should be the main speaker controlling the playback.

        :param api: Api to control the main speaker
        :param name: Name to used for the group
        :param speaker: List of Speaker instances in this group
        """
        self._api = api
        self._name = name
        self._speakers = speakers

    @property
    def ip_address(self):
        """
        :returns: Speaker's ip address
        """
        return self._speakers[0].ip_address

    @property
    def mac_address(self):
        """
        :returns: Speaker's mac address
        """
        return self._speakers[0].mac_address

    @property
    def speakers(self):
        """
        :returns: List of speakers in this group.
        """
        return self._speakers

    def get_name(self):
        """
        :returns: Group's name
        """
        return self._name

    def set_name(self, name):
        """
        Set group name.

        Works only locally.
        todo: investigate if group name can be updated without recreating the group

        :param name: New group name
        """
        self._name = name

    def get_volume(self):
        """
        Get current volume.

        It uses main speaker volume as a reference.

        :returns: int current volume
        """
        return self._speakers[0].get_volume()

    def set_volume(self, volume):
        """
        Set volume for all speakers in the group.

        It uses main speaker's volume as a reference point and updates secondary speakers proportionally.

        :param volume: speaker volume, integer between 0 and 100
        """
        ratio = volume / self._speakers[0].get_volume()

        self._speakers[0].set_volume(volume)

        for speaker in self._speakers[1:]:
            speaker.set_volume(min(100, int(speaker.get_volume() * ratio)))

    def get_sources(self):
        """
        Get all supported sources.

        :returns: List of supported sources.
        """
        return self._speakers[0].get_sources()

    def get_source(self):
        """
        Get currently selected source.

        :returns: selected source string.
        """
        return self._speakers[0].get_source()

    def set_source(self, source):
        """
        Set speaker source.

        :param source: Speaker source, one of returned by get_sources()
        """
        return self._speakers[0].set_source(source)

    def is_muted(self):
        """
        Check if all speakers in this group are muted.

        :returns: True if muted, False otherwise
        """
        for speaker in self._speakers:
            if not speaker.is_muted():
                return False

        return True

    def mute(self):
        """Mute all speakers in this group."""
        for speaker in self._speakers:
            speaker.mute()

    def unmute(self):
        """Unmute all speakers in this group."""
        for speaker in self._speakers:
            speaker.unmute()

    def get_services_names(self):
        """
        Get all supported services names.

        :returns: List of strings
        """
        return self._speakers[0].get_services_names()

    def service(self, name):
        """
        Get service by type

        :returns: Service instance
        """
        return self._speakers[0].service(name)

    @property
    def clock(self):
        """
        Get clock to control time functions.

        :returns: Clock instance
        """
        return ClockGroup([s.clock for s in self._speakers])

    @property
    def equalizer(self):
        """
        Get equalizer to control sound adjustments.

        :returns: Equalizer instance
        """
        return EqualizerGroup([s.equalizer for s in self._speakers])

    @property
    def player(self):
        """
        Get currently active player.

        Use player to control playback e.g. pause, resume, get track info etc.

        :returns: Player instance
        """
        return self._speakers[0].player

    def browser(self, name):
        """
        Get media browser by type

        :returns: Browser instance
        """
        return self._speakers[0].browser(name)

    def group(self, name, speakers):
        """
        Adds speakers to this group.

        This group's main speaker will continue to be the main speaker controlling the playback.

        :param speaker: List of Speaker instances to add to this group
        :returns: This speaker group instance
        """
        if isinstance(speakers, Speaker):
            speakers = [speakers]

        main_speaker = self._speakers[0]
        speakers = self._speakers[1:] + speakers

        speaker_group = main_speaker.group(name, speakers)

        self._name = speaker_group.get_name()
        self._speakers = speaker_group.speakers

        return self

    def ungroup(self):
        """
        Remove all speakers from this group and disband it.
        """
        for speaker in reversed(self._speakers):
            speaker.ungroup()


def speaker_factory(ip_address):
    """
    Factory for Speaker.

    :param ip_address: IP address of the speaker.
    """
    api = SamsungMultiroomApi(ip_address)

    timer = Timer(api)
    alarm = Alarm(api)
    clock = Clock(api, timer, alarm)

    equalizer = Equalizer(api)

    players = [
        DlnaPlayer(api),
        TuneInPlayer(api),
        AppPlayer(api),
    ]
    player_operator = PlayerOperator(api, players)

    service_registry = ServiceRegistry(api)

    return Speaker(api, clock, equalizer, player_operator, service_registry)
