"""Event."""
from ..event import Event


class SpeakerVolumeChangedEvent(Event):
    """Event when speaker volume is adjusted."""

    def __init__(self, volume):
        """
        :param volume: int new volume
        """
        super().__init__('speaker.volume.changed')

        self._volume = volume

    @property
    def volume(self):
        """
        :returns: new volume
        """
        return self._volume

    @classmethod
    def factory(cls, response):
        """
        Factory event from response.

        :returns: SpeakerVolumeChangedEvent instance or None if response is unsupported
        """
        if response.name != 'VolumeLevel':
            return None

        return cls(int(response.data['volume']))
