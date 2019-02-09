"""Event."""
from ..event import Event


class SpeakerServiceEvent(Event):
    """Event when service is changed."""

    def __init__(self, name, service_name):
        """
        :param name: Event name
        :param service_name: Name of the service selected
        """
        super().__init__(name)

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

        :returns: SpeakerServiceEvent instance or None if response is unsupported
        """
        valid_responses_map = {
            'CpChanged': 'speaker.service.changed',
            'SignInStatus': 'speaker.service.logged_in',
            'SignOutStatus': 'speaker.service.logged_out',
        }

        if response.name not in valid_responses_map:
            return None

        return cls(valid_responses_map[response.name], response.data['cpname'])
