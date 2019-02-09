import unittest
from unittest.mock import MagicMock

from samsung_multiroom.event.type.speaker_player import SpeakerPlayerEvent


class TestSpeakerPlayerEvent(unittest.TestCase):

    def test_factory(self):
        responses = {
            'StartPlaybackEvent': 'speaker.player.playback_started',
            'StopPlaybackEvent': 'speaker.player.playback_ended',
            'EndPlaybackEvent': 'speaker.player.playback_ended',
            'PausePlaybackEvent': 'speaker.player.playback_paused',
            'MediaBufferStartEvent': 'speaker.player.buffering_started',
            'MediaBufferEndEvent': 'speaker.player.buffering_ended',
            'OtherResponse': None,
        }

        for response_name, event_name in responses.items():
            response = MagicMock()
            response.name = response_name

            event = SpeakerPlayerEvent.factory(response)

            if event_name:
                self.assertIsInstance(event, SpeakerPlayerEvent)
                self.assertEqual(event.name, event_name)
            else:
                self.assertIsNone(event)
