import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.event import Event


class TestEvent(unittest.TestCase):

    def test_name(self):
        event = Event('speaker.volume.changed')

        self.assertEqual(event.name, 'speaker.volume.changed')
