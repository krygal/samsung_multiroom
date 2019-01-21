"""
Init.
"""
# pylint: disable=C0103
from . import factory
from . import discovery
from .service import REPEAT_ONE, REPEAT_ALL, REPEAT_OFF

# aliases
SamsungMultiroomSpeaker = factory.speaker_factory
SamsungSpeakerDiscovery = discovery.SpeakerDiscovery
