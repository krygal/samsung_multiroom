"""Select the right player for the current source."""
from .player import REPEAT_OFF
from .player import Player
from .player import get_is_supported_function_name
from .player import unsupported


class PlayerOperator(Player):
    """Select the right player for the current source."""

    def __init__(self, api, players=None):
        """
        Initialise player operator.

        :param api: SamsungMultiroomApi instance
        :param players: List of Player instances
        """
        self._api = api
        self._players = []

        for player in (players or []):
            self.add_player(player)

    def add_player(self, player):
        """
        Add player.

        :param player: Player instance
        """
        if not isinstance(player, Player):
            raise ValueError('Player must be a subclass of Player class')

        self._players.append(player)

    def get_player(self):
        """
        Get currently active player based on selected source.

        :returns: Player instance
        """
        func = self._api.get_func()

        function = func['function']
        submode = func['submode']

        for player in self._players:
            if player.is_active(function, submode):
                return player

        return NullPlayer()

    def play(self, playlist):
        """
        Find a suitable player and play a playlist.

        :param playlist: Iterable returning player combatible objects
        :returns: True if playlist was accepted, False otherwise
        """
        for player in self._players:
            if player.play(playlist):
                return True

        return False

    def jump(self, time):
        """
        Advance current playback to specific time.

        :param time: Time from the beginning of the track in seconds
        """
        self.get_player().jump(time)

    def resume(self):
        """Play/resume current track."""
        self.get_player().resume()

    def stop(self):
        """Stop current track and reset position to the beginning."""
        self.get_player().stop()

    def pause(self):
        """Pause current track and retain position."""
        self.get_player().pause()

    def next(self):
        """Play next track in the queue."""
        self.get_player().next()

    def previous(self):
        """Play previous track in the queue."""
        self.get_player().previous()

    def repeat(self, mode):
        """
        Set playback repeat mode.

        :param mode: one of REPEAT_* constants
        """
        self.get_player().repeat(mode)

    def shuffle(self, enabled):
        """
        Enable/disable playback shuffle mode.

        :param enabled: True to enable, False to disable
        """
        self.get_player().shuffle(enabled)

    def get_repeat(self):
        """
        Get playback repeat mode.

        :returns: one of REPEAT_* constants
        """
        return self.get_player().get_repeat()

    def get_shuffle(self):
        """
        Get playback shuffle mode.

        :returns: boolean, True if enabled, False otherwise
        """
        return self.get_player().get_shuffle()

    def get_current_track(self):
        """
        Get current track info.

        :returns: Track instance, or None if unavailable
        """
        return self.get_player().get_current_track()

    def is_active(self, function, submode=None):
        """
        Check if this player is active based on current function/submode.

        :returns: Boolean True if function/submode is supported
        """
        for player in self._players:
            if player.is_active(function, submode):
                return True

        return False

    def __getattribute__(self, name):
        """
        Delegates is_[function_name]_supported to the currently active player.
        """
        if get_is_supported_function_name(name) is None:
            return super().__getattribute__(name)

        return getattr(self.get_player(), name)


class NullPlayer(Player):
    """Catch all player if no others supported current function."""

    @unsupported
    def play(self, playlist):
        """
        Null player is unable to play anything.

        :param playlist: Playlist instance
        :returns: Boolean False
        """
        return False

    @unsupported
    def jump(self, time):
        """Do nothing."""

    @unsupported
    def resume(self):
        """Do nothing."""

    @unsupported
    def stop(self):
        """Do nothing."""

    @unsupported
    def pause(self):
        """Do nothing."""

    @unsupported
    def next(self):
        """Do nothing."""

    @unsupported
    def previous(self):
        """Do nothing."""

    @unsupported
    def repeat(self, mode):
        """Do nothing."""

    @unsupported
    def shuffle(self, enabled):
        """Do nothing."""

    def get_repeat(self):
        """Always off."""
        return REPEAT_OFF

    def get_shuffle(self):
        """Always False."""
        return False

    def get_current_track(self):
        """
        Do nothing.

        :returns: None
        """
        return None

    def is_active(self, function, submode=None):
        """
        Check if this player is active based on current function/submode.

        :returns: Boolean True
        """
        return True
