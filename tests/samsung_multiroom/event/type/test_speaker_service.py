import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.type.speaker_service import SpeakerServiceEvent


class TestSpeakerPlayerEvent(unittest.TestCase):

    def test_factory(self):
        responses = {
            'CpChanged': 'speaker.service.changed',
            'SignInStatus': 'speaker.service.logged_in',
            'SignOutStatus': 'speaker.service.logged_out',
            'OtherResponse': None,
        }

        for response_name, event_name in responses.items():
            response = MagicMock()
            response.name = response_name
            response.data = {'cpname': 'MyService'}

            event = SpeakerServiceEvent.factory(response)

            if event_name:
                self.assertIsInstance(event, SpeakerServiceEvent)
                self.assertEqual(event.name, event_name)
                self.assertEqual(event.service_name, 'MyService')
            else:
                self.assertIsNone(event)
