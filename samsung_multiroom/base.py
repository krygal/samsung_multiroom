"""Speaker interface to control speaker operation."""
import abc


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

    @property
    def event_loop(self):
        """
        Get event loop

        :returns: EventLoop instance
        """
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
