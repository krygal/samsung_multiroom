"""Control speaker's clock functions."""
import abc
import datetime


class ClockBase(metaclass=abc.ABCMeta):
    """
    Clock interface to control time functions of the speaker.
    """

    def set_time(self, speaker_datetime=None):
        """
        Set speaker's current time.

        :param speaker_datetime: Datetime object
        """
        raise NotImplementedError()

    @property
    def alarm(self):
        """
        :returns: Alarm instance
        """
        raise NotImplementedError()

    @property
    def timer(self):
        """
        :returns: Timer instance
        """
        raise NotImplementedError()


class Clock(ClockBase):
    """
    Control time functions of the speaker.
    """

    def __init__(self, api, timer, alarm):
        """
        :param api: SamsungMultiroomApi instance
        """
        self._api = api
        self._timer = timer
        self._alarm = alarm

    def set_time(self, speaker_datetime=None):
        """
        Set speaker's current time.

        :param speaker_datetime: Datetime object
        """
        if speaker_datetime is None:
            speaker_datetime = datetime.datetime.now()

        self._api.set_speaker_time(speaker_datetime)

    @property
    def alarm(self):
        """
        :returns: Alarm instance
        """
        return self._alarm

    @property
    def timer(self):
        """
        :returns: Timer instance
        """
        return self._timer
