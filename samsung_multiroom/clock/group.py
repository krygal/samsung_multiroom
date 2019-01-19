"""Control time functions for the group of the speakers."""
from .clock import ClockBase


class ClockGroup(ClockBase):
    """
    Control time functions for the group of the speakers.

    Due to the nature of alarms and timers, it is only required to use those on the main speaker of the group.
    """

    def __init__(self, clocks):
        """
        :param clocks: List of Clock instances
        """
        self._clocks = clocks

    @property
    def clocks(self):
        """
        :returns: List of Clock instances in group
        """
        return self._clocks

    def set_time(self, speaker_datetime=None):
        """
        Set current time for all speakers in group.

        :param speaker_datetime: Datetime object
        """
        for clock in self._clocks:
            clock.set_time(speaker_datetime)

    @property
    def alarm(self):
        """
        It is not possible to update alarm functions while the speaker is part of a group.

        :returns: Alarm instance of the first clock
        """
        return self._clocks[0].alarm

    @property
    def timer(self):
        """
        :returns: Timer instance of the first clock
        """
        return self._clocks[0].timer
