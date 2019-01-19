import datetime
import unittest
from unittest.mock import MagicMock

from samsung_multiroom.clock import Clock


def get_clock():
    api = MagicMock()
    alarm = MagicMock()
    timer = MagicMock()

    clock = Clock(api, timer, alarm)

    return (clock, api, alarm, timer)


NOW = datetime.datetime(2018, 1, 7, 15, 45, 32)


class TestClock(unittest.TestCase):

    def test_set_time(self):
        clock, api, alarm, timer = get_clock()

        spk_datetime = datetime.datetime.now()

        clock.set_time(spk_datetime)

        api.set_speaker_time.assert_called_once_with(spk_datetime)

    @unittest.mock.patch('datetime.datetime')
    def test_set_time_now(self, dt):
        clock, api, alarm, timer = get_clock()

        dt.now.return_value = NOW

        clock.set_time()

        api.set_speaker_time.assert_called_once_with(NOW)

    def test_timer(self):
        clock, api, alarm, timer = get_clock()

        self.assertEqual(clock.timer, timer)

    def test_alarm(self):
        clock, api, alarm, timer = get_clock()

        self.assertEqual(clock.alarm, alarm)
