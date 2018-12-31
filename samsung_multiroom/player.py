"""Player allows playback control depending on selected source."""
import abc


class PlayerOperator:
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
            if player.is_supported(function, submode):
                return player

        return NullPlayer()


class Player(metaclass=abc.ABCMeta):
    """Controls playback functions."""

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
    def get_current_track(self):
        """
        Get current track info.

        :returns: Track instance, or None if unavailable
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def is_supported(self, function, submode=None):
        """
        Check if this player supports function/submode.

        :returns: Boolean True if function/submode is supported
        """
        raise NotImplementedError()


class DlnaPlayer(Player):
    """Controls player in WIFI+DLNA mode."""

    def __init__(self, api):
        self._api = api

    def resume(self):
        """Play/resume current track."""
        self._api.set_playback_control('resume')

    def stop(self):
        """Stop current track and reset position to the beginning."""
        raise NotImplementedError()

    def pause(self):
        """Pause current track and retain position."""
        self._api.set_playback_control('pause')

    def next(self):
        """Play next track in the queue."""
        self._api.set_trick_mode('next')

    def previous(self):
        """Play previous track in the queue."""
        self._api.set_trick_mode('previous')

    def get_current_track(self):
        """
        Get current track info.

        :returns: Track instance, or None if unavailable
        """
        music_info = self._api.get_music_info()

        track_kwargs = {}

        if 'title' in music_info:
            track_kwargs['title'] = music_info['title']
        if 'artist' in music_info:
            track_kwargs['artist'] = music_info['artist']
        if 'album' in music_info:
            track_kwargs['album'] = music_info['album']
        if 'thumbnail' in music_info and 'http' in music_info['thumbnail']:
            track_kwargs['thumbnail_url'] = music_info['thumbnail']
        if 'timelength' in music_info and music_info['timelength'] is not None:
            (hours, minutes, seconds) = music_info['timelength'].split(':')
            track_kwargs['duration'] = int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
        if 'playtime' in music_info:
            track_kwargs['position'] = int(int(music_info['playtime']) / 1000)

        return Track(**track_kwargs)

    def is_supported(self, function, submode=None):
        """
        Check if this player supports function/submode.

        :returns: Boolean True if function/submode is supported
        """
        return function == 'wifi' and submode == 'dlna'


class TuneInPlayer(Player):
    """Controls player in WIFI+ TuneIn radio mode."""

    def __init__(self, api):
        self._api = api

    def resume(self):
        """Play/resume current track."""
        self._api.set_select_radio()

    def stop(self):
        """Stop current radio."""
        raise NotImplementedError()

    def pause(self):
        """Pause current radio."""
        self._api.set_playback_control('pause')

    def next(self):
        """Play next radio from the preset list."""
        self._previous_next_preset(1)

    def previous(self):
        """Play previous radio from the preset list."""
        self._previous_next_preset(-1)

    def get_current_track(self):
        """
        Get current radio info.

        :returns: Track instance, or None if unavailable
        """
        radio_info = self._api.get_radio_info()

        track_kwargs = {}

        if 'title' in radio_info:
            track_kwargs['artist'] = radio_info['title']
        if 'description' in radio_info:
            track_kwargs['title'] = radio_info['description']
        if 'thumbnail' in radio_info and 'http' in radio_info['thumbnail']:
            track_kwargs['thumbnail_url'] = radio_info['thumbnail']

        track_kwargs['album'] = None
        track_kwargs['duration'] = None
        track_kwargs['position'] = None

        return Track(**track_kwargs)

    def is_supported(self, function, submode=None):
        """
        Check if this player supports function/submode.

        :returns: Boolean True if function/submode is supported
        """
        return function == 'wifi' and submode == 'cp'

    def _previous_next_preset(self, direction):
        if direction not in [-1, 1]:
            raise ValueError('Direction must be either 1 or -1')

        # todo: iterate beyond 10 elements
        presets = self._api.get_preset_list(0, 10)
        presets_count = len(presets)

        if presets_count <= 1:
            return

        # locate current mediaid on the preset list
        radio_info = self._api.get_radio_info()

        current_preset_index = -direction
        if 'presetindex' in radio_info and radio_info['presetindex'] is not None:
            current_preset_index = int(radio_info['presetindex'])

        kind_preset_type = {
            'speaker': 1,
            'my': 0,
        }

        preset_index = (presets_count + max(0, current_preset_index) + direction) % presets_count
        preset = presets[preset_index]
        preset_type = kind_preset_type[preset['kind']]

        self._api.set_play_preset(preset_type, preset_index)
        self._api.set_select_radio()


class NullPlayer(Player):
    """Catch all player if no others supported current function."""

    def resume(self):
        """Do nothing."""

    def stop(self):
        """Do nothing."""

    def pause(self):
        """Do nothing."""

    def next(self):
        """Do nothing."""

    def previous(self):
        """Do nothing."""

    def get_current_track(self):
        """
        Do nothing.

        :returns: None
        """
        return None

    def is_supported(self, function, submode=None):
        """
        Check if this player supports function/submode.

        :returns: Boolean True
        """
        return True


class Track:
    """Defines a media track on the playlist."""

    def __init__(self, title, artist, album, duration, position, thumbnail_url):
        self._title = title
        self._album = album
        self._duration = duration
        self._artist = artist
        self._position = position
        self._thumbnail_url = thumbnail_url

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
