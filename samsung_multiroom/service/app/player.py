"""Generic music streaming app service player."""
from ..player import REPEAT_OFF
from ..player import Player
from ..player import Track
from ..player import init_track_kwargs
from ..player import unsupported


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

    @unsupported
    def jump(self, time):
        """
        Not supported for app.

        :param time: Time from the beginning of the track in seconds
        """

    def resume(self):
        """Play/resume current track."""
        self._api.set_playback_control('play')

    @unsupported
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

    @unsupported
    def repeat(self, mode):
        """Not supported for apps."""

    @unsupported
    def shuffle(self, enabled):
        """Not supported for apps."""

    def get_repeat(self):
        """Not supported for apps."""
        return REPEAT_OFF

    def get_shuffle(self):
        """Not supported for apps."""
        return False

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

        track_kwargs = init_track_kwargs('app_audio')

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

    def is_active(self, function, submode=None):
        """
        Check if this player is active based on current function/submode.

        :returns: Boolean True if function/submode is supported
        """
        return function == 'wifi' and submode == 'cp'
