import datetime
import unittest
from unittest.mock import MagicMock

from samsung_multiroom.clock import ClockGroup


def _get_clock_group():
    clocks = [
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]

    clock_group = ClockGroup(clocks)

    return (clock_group, clocks)


class TestClockGroup(unittest.TestCase):

    def test_set_time_sets_all_clocks(self):
        clock_group, clocks = _get_clock_group()

        dt = datetime.datetime.now()

        clock_group.set_time(dt)

        for clock in clocks:
            clock.set_time.assert_called_once_with(dt)

    def test_alarm_returns_first_clock_alarm(self):
        clock_group, clocks = _get_clock_group()
        clocks[0].alarm = MagicMock()

        alarm = clock_group.alarm

        self.assertEqual(alarm, clocks[0].alarm)

    def test_timer_returns_first_clock_timer(self):
        clock_group, clocks = _get_clock_group()
        clocks[0].timer = MagicMock()

        timer = clock_group.timer

        self.assertEqual(timer, clocks[0].timer)
