"""Event."""
from ..event import Event


class SpeakerPlayerEvent(Event):
    """Event when player status changes."""

    @classmethod
    def factory(cls, response):
        """
        Factory event from response.

        :returns: SpeakerPlayerEvent instance or None if response is unsupported
        """
        valid_responses_map = {
            'StartPlaybackEvent': 'speaker.player.playback_started',
            'StopPlaybackEvent': 'speaker.player.playback_ended',
            'EndPlaybackEvent': 'speaker.player.playback_ended',
            'PausePlaybackEvent': 'speaker.player.playback_paused',
            'MediaBufferStartEvent': 'speaker.player.buffering_started',
            'MediaBufferEndEvent': 'speaker.player.buffering_ended',
        }

        if response.name not in valid_responses_map:
            return None

        return cls(valid_responses_map[response.name])
