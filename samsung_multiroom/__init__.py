"""
Init.
"""
# pylint: disable=C0103
from . import factory
from . import discovery

# aliases
SamsungMultiroomSpeaker = factory.speaker_factory
SamsungSpeakerDiscovery = discovery.SpeakerDiscovery
