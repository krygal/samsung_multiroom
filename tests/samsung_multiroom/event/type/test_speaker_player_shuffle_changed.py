import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.type.speaker_player_shuffle_changed import SpeakerPlayerShuffleChangedEvent


class TestSpeakershuffleChangedEvent(unittest.TestCase):

    def test_factory(self):
        response = MagicMock()
        response.name = 'ShuffleMode'
        response.data = {'shuffle': 'on'}

        event = SpeakerPlayerShuffleChangedEvent.factory(response)

        self.assertIsInstance(event, SpeakerPlayerShuffleChangedEvent)
        self.assertEqual(event.shuffle, True)

    def test_factory_returns_none(self):
        response = MagicMock()
        response.name = 'OtherResponse'

        event = SpeakerPlayerShuffleChangedEvent.factory(response)

        self.assertEqual(event, None)
