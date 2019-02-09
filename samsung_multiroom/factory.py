"""Factory for Speaker."""
import uuid

from .api import ApiStream
from .api import SamsungMultiroomApi
from .clock import Alarm
from .clock import Clock
from .clock import Timer
from .equalizer import Equalizer
from .event import EventLoop
from .service import PlayerOperator
from .service import ServiceRegistry
from .service.app import AppPlayer
from .service.dlna import DlnaPlayer
from .service.tunein import TuneInPlayer
from .speaker import Speaker


def speaker_factory(ip_address):
    """
    Factory for Speaker.

    :param ip_address: IP address of the speaker.
    """
    user = str(uuid.uuid1())
    api = SamsungMultiroomApi(user, ip_address)
    api_stream = ApiStream(user, ip_address)

    timer = Timer(api)
    alarm = Alarm(api)
    clock = Clock(api, timer, alarm)

    equalizer = Equalizer(api)

    players = [
        DlnaPlayer(api),
        TuneInPlayer(api),
        AppPlayer(api),
    ]
    player_operator = PlayerOperator(api, players)

    service_registry = ServiceRegistry(api)

    event_loop = EventLoop(api_stream)

    return Speaker(api, event_loop, clock, equalizer, player_operator, service_registry)
