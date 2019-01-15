"""Player allows playback control depending on selected source."""
import abc

from .api import paginator


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
            if player.is_supported(function, submode):
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

    def get_current_track(self):
        """
        Get current track info.

        :returns: Track instance, or None if unavailable
        """
        return self.get_player().get_current_track()

    def is_supported(self, function, submode=None):
        """
        Check if this player supports function/submode.

        :returns: Boolean True if function/submode is supported
        """
        for player in self._players:
            if player.is_supported(function, submode):
                return True

        return False


class DlnaPlayer(Player):
    """Controls player in WIFI+DLNA mode."""

    def __init__(self, api):
        self._api = api

    def play(self, playlist):
        """
        Enqueue and play a playlist.

        Playlist items must be an object with following attributes:
        - object_id - object id
        - object_type - must be 'dlna_audio'
        - title - track title
        - artist - track artist
        - thumbnail_url - thumbnail URL
        - device_udn - DLNA device UDN

        :param playlist: Iterable returning player combatible objects
        :returns: True if playlist was accepted, False otherwise
        """
        items = []
        for track in playlist:
            if track.object_type not in ['dlna_audio']:
                continue

            items.append({
                'object_id': track.object_id,
                'title': track.title,
                'artist': track.artist,
                'thumbnail': track.thumbnail_url,
                'device_udn': track.device_udn,
            })

        if items:
            self._api.set_playlist_playback_control(items)
            return True

        return False

    def jump(self, time):
        """
        Advance current playback to specific time.

        :param time: Time from the beginning of the track in seconds
        """
        self._api.set_search_time(time)

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

        track_kwargs = {
            'title': None,
            'artist': None,
            'album': None,
            'duration': None,
            'position': None,
            'thumbnail_url': None,
            'metadata': {
                'object_id': None,
                'object_type': 'dlna_audio',
            }
        }

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
        if 'device_udn' in music_info:
            track_kwargs['metadata']['device_udn'] = music_info['device_udn']
        if 'objectid' in music_info:
            track_kwargs['metadata']['object_id'] = music_info['objectid']

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

    def play(self, playlist):
        """
        Play first radio from a playlist.

        Playlist items must be an object with following attributes:
        - object_id - object id
        - object_type - must be 'tunein_radio'
        - title - radio name

        :param playlist: Iterable returning player combatible objects
        :returns: True if playlist was accepted, False otherwise
        """
        for radio in playlist:
            if radio.object_type not in ['tunein_radio']:
                continue

            self._api.set_play_select(radio.object_id)
            return True

        return False

    def jump(self, time):
        """
        Not supported for radios.

        :param time: Time from the beginning of the track in seconds
        """

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

        track_kwargs = {
            'title': None,
            'artist': None,
            'album': None,
            'duration': None,
            'position': None,
            'thumbnail_url': None,
            'metadata': {
                'object_id': None,
                'object_type': 'tunein_radio',
            }
        }

        if 'title' in radio_info:
            track_kwargs['artist'] = radio_info['title']
        if 'description' in radio_info:
            track_kwargs['title'] = radio_info['description']
        if 'thumbnail' in radio_info and 'http' in radio_info['thumbnail']:
            track_kwargs['thumbnail_url'] = radio_info['thumbnail']

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

        presets = list(paginator(self._api.get_preset_list, 0, 30))
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


class AppPlayer(Player):
    """Controls player in WIFI+cp mode."""

    def __init__(self, api):
        self._api = api

    def play(self, playlist):
        """
        Enqueue and play a playlist.

        Playlist items must be an object with following attributes:
        - object_id - object id
        - object_type - must be 'app_audio'

        :param playlist: Iterable returning player combatible objects
        :returns: True if playlist was accepted, False otherwise
        """
        item_ids = []
        for track in playlist:
            if track.object_type not in ['app_audio']:
                continue

            item_ids.append(track.object_id)

        if item_ids:
            self._api.set_play_select(item_ids)
            return True

        return False

    def jump(self, time):
        """
        Not supported for app.

        :param time: Time from the beginning of the track in seconds
        """

    def resume(self):
        """Play/resume current track."""
        self._api.set_playback_control('play')

    def stop(self):
        """Stop current track and reset position to the beginning."""
        raise NotImplementedError()

    def pause(self):
        """Pause current track and retain position."""
        self._api.set_playback_control('pause')

    def next(self):
        """Play next track in the queue."""
        self._api.set_skip_current_track()

    def previous(self):
        """Play previous track in the queue."""
        playlist = self._api.get_cp_player_playlist()

        for i, playlist_item in enumerate(playlist):
            if '@currentplaying' in playlist_item and playlist_item['@currentplaying'] == '1':
                previous_index = max(0, i - 1)

                self._api.set_play_cp_playlist_track(playlist[previous_index]['contentid'])

    def get_current_track(self):
        """
        Get current track info.

        :returns: Track instance, or None if unavailable
        """
        playlist = self._api.get_cp_player_playlist()
        try:
            playlist_item = [p for p in playlist if '@currentplaying' in p and p['@currentplaying'] == '1'][0]
        except KeyError:
            return None

        track_kwargs = {
            'title': None,
            'artist': None,
            'album': None,
            'duration': None,
            'position': None,
            'thumbnail_url': None,
            'metadata': {
                'object_id': None,
                'object_type': 'app_audio',
            }
        }

        if 'title' in playlist_item:
            track_kwargs['title'] = playlist_item['title']
        if 'artist' in playlist_item:
            track_kwargs['artist'] = playlist_item['artist']
        if 'album' in playlist_item:
            track_kwargs['album'] = playlist_item['album']
        if 'thumbnail' in playlist_item and 'http' in playlist_item['thumbnail']:
            track_kwargs['thumbnail_url'] = playlist_item['thumbnail']
        if 'mediaid' in playlist_item:
            track_kwargs['metadata']['object_id'] = playlist_item['mediaid']

        play_time = self._api.get_current_play_time()

        if 'timelength' in play_time and play_time['timelength'] is not None:
            track_kwargs['duration'] = int(play_time['timelength'])
        if 'playtime' in play_time:
            track_kwargs['position'] = int(play_time['playtime'])

        return Track(**track_kwargs)

    def is_supported(self, function, submode=None):
        """
        Check if this player supports function/submode.

        :returns: Boolean True if function/submode is supported
        """
        return function == 'wifi' and submode == 'cp'


class NullPlayer(Player):
    """Catch all player if no others supported current function."""

    def play(self, playlist):
        """
        Null player is unable to play anything.

        :param playlist: Playlist instance
        :returns: Boolean False
        """
        return False

    def jump(self, time):
        """Do nothing."""

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
