"""
Init.
"""
# pylint: disable=C0103
from . import core
from .api import SamsungMultiroomApi
from .api import SamsungMultiroomApiException
from .player import PlayerOperator, DlnaPlayer, TuneInPlayer


# factory
def SamsungMultiroomSpeaker(ip_address):
    """
    Factory for Speaker.

    :param ip_address: IP address of the speaker.
    """
    api = SamsungMultiroomApi(ip_address)
    player_operator = PlayerOperator(api)
    player_operator.add_player(DlnaPlayer(api))
    player_operator.add_player(TuneInPlayer(api))

    return core.Speaker(api, player_operator)
