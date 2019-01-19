"""Control timer to put speaker into sleep mode."""


class Timer:
    """
    Control timer to put speaker into sleep mode.
    """

    def __init__(self, api):
        """
        :param api: SamsungMultiroomApi instance
        """
        self._api = api

    def start(self, delay):
        """
        Set timer to put speaker into sleep mode after delay.

        :param delay: Delay in seconds
        """
        self._api.set_sleep_timer('start', delay)

    def stop(self):
        """
        Stop the timer.
        """
        self._api.set_sleep_timer('off', 0)

    def get_remaining_time(self):
        """
        :returns: Remaining timer seconds, or 0 if not enabled.
        """
        return int(self._api.get_sleep_timer()['sleeptime'])
