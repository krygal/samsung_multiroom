"""Entry control for speaker operation."""
from .base import SpeakerBase
from .group import SpeakerGroup


class Speaker(SpeakerBase):
    """Entry control for speaker operation."""

    def __init__(self, api, event_loop, clock, equalizer, player_operator, service_registry):
        """
        Initialise the speaker.

        :param api: SamsungMultiroomApi instance
        :param event_loop: EventLoop instance
        :param clock: Clock instance
        :param equalizer: Equalizer instance
        :param player_operator: PlayerOperator instance
        :param service_registry: ServiceRegistry instance
        """
        self._api = api
        self._event_loop = event_loop
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

    @property
    def event_loop(self):
        """
        Get event loop

        :returns: EventLoop instance
        """
        return self._event_loop

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
