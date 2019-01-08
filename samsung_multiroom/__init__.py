"""
Init.
"""
# pylint: disable=C0103
from . import core
from .api import SamsungMultiroomApi
from .api import SamsungMultiroomApiException
from .equalizer import Equalizer
from .player import PlayerOperator, DlnaPlayer, TuneInPlayer
from .browser import DlnaBrowser, TuneInBrowser
from .clock import Clock, Timer, Alarm


def SamsungMultiroomSpeaker(ip_address):
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
    ]
    player_operator = PlayerOperator(api, players)

    browsers = [
        DlnaBrowser(api),
        TuneInBrowser(api),
    ]

    return core.Speaker(api, clock, equalizer, player_operator, browsers)
