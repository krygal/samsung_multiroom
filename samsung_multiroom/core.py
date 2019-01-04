"""Entry control for speaker operation. """


class Speaker:
    """Entry control for speaker operation."""

    def __init__(self, api, player_operator, browsers=None):
        """
        Initialise the speaker.

        :param api: SamsungMultiroomApi instance
        :param player_operator: PlayerOperator instance
        :param browsers: List of Browser instances
        """
        self._api = api
        self._player_operator = player_operator
        self._browsers = {}

        for browser in (browsers or []):
            self._browsers[browser.get_name()] = browser

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

    def get_player(self):
        """
        Get currently active player.

        Use player to control playback e.g. pause, resume, get track info etc.

        :returns: Player instance
        """
        return self._player_operator

    def get_browser(self, name):
        """
        Get media browser by type

        :returns: Browser instance
        """
        return self._browsers[name]
