"""Event."""
from ..event import Event


class SpeakerMuteChangedEvent(Event):
    """Event when speaker mute state changes."""

    def __init__(self, muted):
        """
        :param muted: Boolean
        """
        super().__init__('speaker.mute.changed')

        self._muted = muted

    @property
    def muted(self):
        """
        :returns: Mute state, True if muted
        """
        return self._muted

    @classmethod
    def factory(cls, response):
        """
        Factory event from response.

        :returns: SpeakerMuteChangedEvent instance or None if response is unsupported
        """
        if response.name != 'MuteStatus':
            return None

        return cls(response.data['mute'] == 'on')
