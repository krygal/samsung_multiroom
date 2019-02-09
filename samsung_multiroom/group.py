"""Speaker group."""
from .base import SpeakerBase
from .clock import ClockGroup
from .equalizer import EqualizerGroup


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

        :param name: New group name
        """
        self._api.set_group_name(name)
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

    @property
    def event_loop(self):
        """
        Get event loop

        :returns: EventLoop instance
        """
        return self._speakers[0].event_loop

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
        if isinstance(speakers, SpeakerBase):
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
