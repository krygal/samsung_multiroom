import unittest
from unittest.mock import MagicMock

from samsung_multiroom.player import NullPlayer
from samsung_multiroom.player import Player
from samsung_multiroom.player import PlayerOperator


def get_mocks():
    api = MagicMock()
    api.get_func.return_value = {'function': 'test_function', 'submode': 'test_submode'}

    player1 = MagicMock(spec=Player, name='player1')
    player1.is_supported.return_value = False
    player2 = MagicMock(spec=Player, name='player2')
    player2.is_supported.return_value = True

    player_operator = PlayerOperator(api, [player1, player2])

    return (player_operator, api, [player1, player2])


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

    def test_get_play(self):
        api = MagicMock()
        api.get_func.return_value = {'function': 'test_function', 'submode': 'test_submode'}

        player1 = MagicMock(spec=Player, name='player1')
        player1.play.return_value = False
        player2 = MagicMock(spec=Player, name='player2')
        player2.play.return_value = True
        player3 = MagicMock(spec=Player, name='player3')
        player3.play.return_value = True

        playlist = MagicMock()

        player_operator = PlayerOperator(api, [player1, player2, player3])
        self.assertTrue(player_operator.play(playlist))

        player1.play.assert_called_once_with(playlist)
        player2.play.assert_called_once_with(playlist)
        player3.play.assert_not_called()

    def test_get_play_returns_false(self):
        api = MagicMock()
        api.get_func.return_value = {'function': 'test_function', 'submode': 'test_submode'}

        player1 = MagicMock(spec=Player, name='player1')
        player1.play.return_value = False
        player2 = MagicMock(spec=Player, name='player2')
        player2.play.return_value = False
        player3 = MagicMock(spec=Player, name='player3')
        player3.play.return_value = False

        playlist = MagicMock()

        player_operator = PlayerOperator(api, [player1, player2, player3])
        self.assertFalse(player_operator.play(playlist))

        player1.play.assert_called_once_with(playlist)
        player2.play.assert_called_once_with(playlist)
        player3.play.assert_called_once_with(playlist)

    def test_jump(self):
        player_operator, api, players = get_mocks()
        player_operator.jump(50)

        players[0].jump.assert_not_called()
        players[1].jump.assert_called_once_with(50)

    def test_resume(self):
        player_operator, api, players = get_mocks()
        player_operator.resume()

        players[0].resume.assert_not_called()
        players[1].resume.assert_called_once()

    def test_stop(self):
        player_operator, api, players = get_mocks()
        player_operator.stop()

        players[0].stop.assert_not_called()
        players[1].stop.assert_called_once()

    def test_pause(self):
        player_operator, api, players = get_mocks()
        player_operator.pause()

        players[0].pause.assert_not_called()
        players[1].pause.assert_called_once()

    def test_next(self):
        player_operator, api, players = get_mocks()
        player_operator.next()

        players[0].next.assert_not_called()
        players[1].next.assert_called_once()

    def test_previous(self):
        player_operator, api, players = get_mocks()
        player_operator.previous()

        players[0].previous.assert_not_called()
        players[1].previous.assert_called_once()

    def test_get_current_track(self):
        player_operator, api, players = get_mocks()

        track = MagicMock()
        players[1].get_current_track.return_value = track

        self.assertEqual(player_operator.get_current_track(), track)

        players[0].get_current_track.assert_not_called()
        players[1].get_current_track.assert_called_once()

    def test_is_supported(self):
        player_operator, api, players = get_mocks()
        self.assertTrue(player_operator.is_supported('test_function', 'test_submode'))

        players[0].is_supported.assert_called_once_with('test_function', 'test_submode')
        players[1].is_supported.assert_called_once_with('test_function', 'test_submode')

    def test_is_supported_returns_false(self):
        player_operator, api, players = get_mocks()

        players[0].is_supported.return_value = False
        players[1].is_supported.return_value = False

        self.assertFalse(player_operator.is_supported('test_function', 'test_submode'))

        players[0].is_supported.assert_called_once_with('test_function', 'test_submode')
        players[1].is_supported.assert_called_once_with('test_function', 'test_submode')
