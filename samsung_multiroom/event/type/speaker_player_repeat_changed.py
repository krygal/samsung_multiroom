"""Event."""
from ...service.player import REPEAT_ALL
from ...service.player import REPEAT_OFF
from ...service.player import REPEAT_ONE
from ..event import Event


class SpeakerPlayerRepeatChangedEvent(Event):
    """Event when player's repeat state changes."""

    def __init__(self, repeat):
        """
        :param repeat: one of REPEAT_ constants
        """
        super().__init__('speaker.player.repeat.changed')

        self._repeat = repeat

    @property
    def repeat(self):
        """
        :returns: repeat state, True if repeat is on
        """
        return self._repeat

    @classmethod
    def factory(cls, response):
        """
        Factory event from response.

        :returns: SpeakerPlayerRepeatChangedEvent instance or None if response is unsupported
        """
        if response.name != 'RepeatMode':
            return None

        mode_map = {
            'all': REPEAT_ALL,
            'one': REPEAT_ONE,
            'off': REPEAT_OFF,
        }

        return cls(mode_map[response.data['repeat']])
