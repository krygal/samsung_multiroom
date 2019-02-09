"""Event."""
from ..event import Event


class SpeakerPlayerShuffleChangedEvent(Event):
    """Event when player's shuffle state changes."""

    def __init__(self, shuffle):
        """
        :param shuffle: Boolean
        """
        super().__init__('speaker.player.shuffle.changed')

        self._shuffle = shuffle

    @property
    def shuffle(self):
        """
        :returns: Shuffle state, True if shuffle is on
        """
        return self._shuffle

    @classmethod
    def factory(cls, response):
        """
        Factory event from response.

        :returns: SpeakerPlayerShuffleChangedEvent instance or None if response is unsupported
        """
        if response.name != 'ShuffleMode':
            return None

        return cls(response.data['shuffle'] == 'on')
