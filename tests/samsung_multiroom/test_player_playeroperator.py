import unittest
from unittest.mock import MagicMock

from samsung_multiroom.player import NullPlayer
from samsung_multiroom.player import Player
from samsung_multiroom.player import PlayerOperator


class TestPlayerOperator(unittest.TestCase):

    def test_only_player_instances_are_allowed(self):
        api = MagicMock()

        player1 = MagicMock(spec=Player, name='player1')
        player2 = MagicMock(name='player2')

        self.assertRaises(ValueError, PlayerOperator, api, [player1, player2])

    def test_get_player_returns_supporting_player(self):
        api = MagicMock()
        api.get_func.return_value = {'function': 'test_function', 'submode': 'test_submode'}

        player1 = MagicMock(spec=Player, name='player1')
        player1.is_supported.return_value = False
        player2 = MagicMock(spec=Player, name='player2')
        player2.is_supported.return_value = True

        player_operator = PlayerOperator(api, [player1, player2])
        player = player_operator.get_player()

        self.assertEqual(player, player2)
        player1.is_supported.assert_called_once_with('test_function', 'test_submode')
        player2.is_supported.assert_called_once_with('test_function', 'test_submode')

    def test_get_player_returns_nullplayer_if_no_supported(self):
        api = MagicMock()
        api.get_func.return_value = {'function': 'test_function', 'submode': 'test_submode'}

        player1 = MagicMock(spec=Player, name='player1')
        player1.is_supported.return_value = False
        player2 = MagicMock(spec=Player, name='player2')
        player2.is_supported.return_value = False

        player_operator = PlayerOperator(api, [player1, player2])
        player = player_operator.get_player()

        self.assertIsInstance(player, NullPlayer)
        player1.is_supported.assert_called_once_with('test_function', 'test_submode')
        player2.is_supported.assert_called_once_with('test_function', 'test_submode')
