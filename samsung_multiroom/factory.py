"""Factory for Speaker."""
from .api import SamsungMultiroomApi
from .clock import Alarm
from .clock import Clock
from .clock import Timer
from .equalizer import Equalizer
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
    api = SamsungMultiroomApi(ip_address)

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

    return Speaker(api, clock, equalizer, player_operator, service_registry)
