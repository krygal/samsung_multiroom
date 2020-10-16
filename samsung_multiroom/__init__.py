"""
Init.
"""
# pylint: disable=C0103
from . import discovery
from . import factory
from .service import REPEAT_ALL
from .service import REPEAT_OFF
from .service import REPEAT_ONE

# aliases
SamsungMultiroomSpeaker = factory.speaker_factory
SamsungSpeakerDiscovery = discovery.SpeakerDiscovery
