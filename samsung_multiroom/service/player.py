"""Player allows playback control depending on selected source."""
import abc

# repeat mode constants
REPEAT_ONE = 'one'
REPEAT_ALL = 'all'
REPEAT_OFF = 'off'


class Player(metaclass=abc.ABCMeta):
    """Player interface to control playback functions."""

    @abc.abstractmethod
    def play(self, playlist):
        """
        Enqueue and play a playlist.

        Player may choose to not play the playlist if it's not compatible with this player. For instance you can't
        play DLNA source tracks using TuneIn player. If player is unable to play the playlist it must return False.

        :param playlist: Iterable returning player combatible objects
        :returns: True if playlist was accepted, False otherwise
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def jump(self, time):
        """
        Advance current playback to specific time.

        :param time: Time from the beginning of the track in seconds
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def resume(self):
        """Play/resume current track."""
        raise NotImplementedError()

    @abc.abstractmethod
    def stop(self):
        """Stop current track and reset position to the beginning."""
        raise NotImplementedError()

    @abc.abstractmethod
    def pause(self):
        """Pause current track and retain position."""
        raise NotImplementedError()

    @abc.abstractmethod
    def next(self):
        """Play next track in the queue."""
        raise NotImplementedError()

    @abc.abstractmethod
    def previous(self):
        """Play previous track in the queue."""
        raise NotImplementedError()

    @abc.abstractmethod
    def repeat(self, mode):
        """
        Set playback repeat mode.

        :param mode: one of REPEAT_* constants
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def shuffle(self, enabled):
        """
        Enable/disable playback shuffle mode.

        :param enabled: True to enable, False to disable
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_repeat(self):
        """
        Get playback repeat mode.

        :returns: one of REPEAT_* constants
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_shuffle(self):
        """
        Get playback shuffle mode.

        :returns: boolean, True if enabled, False otherwise
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_current_track(self):
        """
        Get current track info.

        :returns: Track instance, or None if unavailable
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def is_active(self, function, submode=None):
        """
        Check if this player is active based on current function/submode.

        :returns: Boolean True if function/submode is supported
        """
        raise NotImplementedError()

    def __getattribute__(self, name):
        """
        Magic is_[function]_supported method.

        Function can be any Player method. In order to mark method as unsupported, use @unsupported decorator.

        Example:
            MyPlayer(Player):
                @unsupported
                def play(self, playlist):
                    return False

            player = MyPlayer()
            player.is_play_supported() # returns False
        """
        try:
            return super().__getattribute__(name)
        except AttributeError:
            function_name = get_is_supported_function_name(name)

            if not function_name:
                raise

            if not hasattr(self, function_name):
                raise

            function = getattr(self, function_name)
            if not hasattr(function, '__is_supported__'):
                return lambda: True

            return lambda: bool(function.__is_supported__)


class Track:
    """Defines a media track on the playlist."""

    def __init__(self, title, artist, album, duration, position, thumbnail_url, metadata=None):
        self._title = title
        self._artist = artist
        self._album = album
        self._duration = duration
        self._position = position
        self._thumbnail_url = thumbnail_url
        self._metadata = metadata or {}

    @property
    def title(self):
        """
        :returns: Title of the current track
        """
        return self._title

    @property
    def artist(self):
        """
        :returns: Artist of the current track
        """
        return self._artist

    @property
    def album(self):
        """
        :returns: Album title of the current track
        """
        return self._album

    @property
    def duration(self):
        """
        :returns: Duration in seconds
        """
        return self._duration

    @property
    def position(self):
        """
        :returns: Current playback position in seconds
        """
        return self._position

    @property
    def thumbnail_url(self):
        """
        :returns: URL of the track thumbnail
        """
        return self._thumbnail_url

    def __getattr__(self, name):
        """
        :returns: Metadata item value
        """
        if name in self._metadata:
            return self._metadata[name]

        return None


def init_track_kwargs(object_type):
    """
    :returns: kwargs dict fro Track initialisation
    """
    return {
        'title': None,
        'artist': None,
        'album': None,
        'duration': None,
        'position': None,
        'thumbnail_url': None,
        'metadata': {
            'object_id': None,
            'object_type': object_type,
        }
    }


def unsupported(function):
    """Decorator to mark player function as unsupported."""
    function.__is_supported__ = False

    return function


def get_is_supported_function_name(name):
    """
    :param name: function name
    :returns: Function name from is_[function_name]_supported structure, None otherwise
    """
    import re

    pattern = re.compile(r'^is_(\w+)_supported$')
    matches = pattern.findall(name)

    if not matches:
        return None

    return matches[0]
