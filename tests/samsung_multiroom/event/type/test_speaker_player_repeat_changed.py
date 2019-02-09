import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.type.speaker_player_repeat_changed import SpeakerPlayerRepeatChangedEvent
from samsung_multiroom.service.player import REPEAT_ALL


class TestSpeakerrepeatChangedEvent(unittest.TestCase):

    def test_factory(self):
        response = MagicMock()
        response.name = 'RepeatMode'
        response.data = {'repeat': 'all'}

        event = SpeakerPlayerRepeatChangedEvent.factory(response)

        self.assertIsInstance(event, SpeakerPlayerRepeatChangedEvent)
        self.assertEqual(event.repeat, REPEAT_ALL)

    def test_factory_returns_none(self):
        response = MagicMock()
        response.name = 'OtherResponse'

        event = SpeakerPlayerRepeatChangedEvent.factory(response)

        self.assertEqual(event, None)
