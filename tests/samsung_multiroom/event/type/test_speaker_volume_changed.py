import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.type.speaker_volume_changed import SpeakerVolumeChangedEvent


class TestSpeakerVolumeChangedEvent(unittest.TestCase):

    def test_factory(self):
        response = MagicMock()
        response.name = 'VolumeLevel'
        response.data = {'volume': '25'}

        event = SpeakerVolumeChangedEvent.factory(response)

        self.assertIsInstance(event, SpeakerVolumeChangedEvent)
        self.assertEqual(event.volume, 25)

    def test_factory_returns_none(self):
        response = MagicMock()
        response.name = 'OtherResponse'

        event = SpeakerVolumeChangedEvent.factory(response)

        self.assertEqual(event, None)
