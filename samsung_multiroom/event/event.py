"""Generic event."""


class Event:
    """Generic event."""

    def __init__(self, name):
        """
        :param name: Name of event as defined in Events class
        """
        self._name = name

    @property
    def name(self):
        """
        :returns: Name of event
        """
        return self._name
