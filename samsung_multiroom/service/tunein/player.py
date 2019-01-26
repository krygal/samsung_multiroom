"""TuneIn service player."""
from ...api import paginator
from ..player import REPEAT_OFF
from ..player import Player
from ..player import Track
from ..player import init_track_kwargs
from ..player import unsupported


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

    @unsupported
    def jump(self, time):
        """
        Not supported for radios.

        :param time: Time from the beginning of the track in seconds
        """

    def resume(self):
        """Play/resume current track."""
        self._api.set_select_radio()

    @unsupported
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

    @unsupported
    def repeat(self, mode):
        """Not supported for radio."""

    @unsupported
    def shuffle(self, enabled):
        """Not supported for radio."""

    def get_repeat(self):
        """Not supported for radio."""
        return REPEAT_OFF

    def get_shuffle(self):
        """Not supported for radio."""
        return False

    def get_current_track(self):
        """
        Get current radio info.

        :returns: Track instance, or None if unavailable
        """
        radio_info = self._api.get_radio_info()

        track_kwargs = init_track_kwargs('tunein_radio')

        if 'title' in radio_info:
            track_kwargs['artist'] = radio_info['title']
        if 'description' in radio_info:
            track_kwargs['title'] = radio_info['description']
        if 'thumbnail' in radio_info and 'http' in radio_info['thumbnail']:
            track_kwargs['thumbnail_url'] = radio_info['thumbnail']

        return Track(**track_kwargs)

    def is_active(self, function, submode=None):
        """
        Check if this player is active based on current function/submode.

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
