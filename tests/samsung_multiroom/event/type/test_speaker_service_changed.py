import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.type.speaker_service_changed import SpeakerServiceChangedEvent


class TestSpeakerServiceChanged(unittest.TestCase):

    def test_factory(self):
        response = MagicMock()
        response.name = 'CpChanged'
        response.data = {'cpname': 'MyService'}

        event = SpeakerServiceChangedEvent.factory(response)

        self.assertIsInstance(event, SpeakerServiceChangedEvent)
        self.assertEqual(event.service_name, 'MyService')

    def test_factory_returns_none(self):
        response = MagicMock()
        response.name = 'OtherResponse'

        event = SpeakerServiceChangedEvent.factory(response)

        self.assertEqual(event, None)
