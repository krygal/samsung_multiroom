import unittest
from unittest.mock import MagicMock

from samsung_multiroom.clock import Timer


def get_timer():
    api = MagicMock()

    timer = Timer(api)

    return (timer, api)


class TestTimer(unittest.TestCase):

    def test_start(self):
        timer, api = get_timer()

        timer.start(300)

        api.set_sleep_timer.assert_called_once_with('start', 300)

    def test_stop(self):
        timer, api = get_timer()

        timer.stop()

        api.set_sleep_timer.assert_called_once_with('off', 0)

    def test_get_remaining_time(self):
        timer, api = get_timer()

        api.get_sleep_timer.return_value = {
            'sleepoption': 'start',
            'sleeptime': '270',
        }

        remaining_time = timer.get_remaining_time()

        self.assertEqual(remaining_time, 270)
