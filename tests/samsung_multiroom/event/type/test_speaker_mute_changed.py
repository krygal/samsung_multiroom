import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.type.speaker_mute_changed import SpeakerMuteChangedEvent


class TestSpeakerMuteChangedEvent(unittest.TestCase):

    def test_factory(self):
        response = MagicMock()
        response.name = 'MuteStatus'
        response.data = {'mute': 'on'}

        event = SpeakerMuteChangedEvent.factory(response)

        self.assertIsInstance(event, SpeakerMuteChangedEvent)
        self.assertEqual(event.muted, True)

    def test_factory_returns_none(self):
        response = MagicMock()
        response.name = 'OtherResponse'

        event = SpeakerMuteChangedEvent.factory(response)

        self.assertEqual(event, None)
