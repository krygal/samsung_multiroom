"""Event."""
from ..event import Event


class SpeakerServiceChangedEvent(Event):
    """Event when service is changed."""

    def __init__(self, service_name):
        """
        :param service_name: Name of the service selected
        """
        super().__init__('speaker.service.changed')

        self._service_name = service_name

    @property
    def service_name(self):
        """
        :returns: Name of the service selected
        """
        return self._service_name

    @classmethod
    def factory(cls, response):
        """
        Factory event from response.

        :returns: SpeakerServiceChangedEvent instance or None if response is unsupported
        """
        if response.name != 'CpChanged':
            return None

        return cls(response.data['cpname'])
