import unittest
from unittest.mock import MagicMock

from samsung_multiroom.service import REPEAT_OFF
from samsung_multiroom.service import REPEAT_ONE
from samsung_multiroom.service.player_operator import NullPlayer


class TestNullPlayer(unittest.TestCase):

    def test_is_supported(self):
        player = NullPlayer()

        self.assertFalse(player.is_play_supported())
        self.assertFalse(player.is_jump_supported())
        self.assertFalse(player.is_resume_supported())
        self.assertFalse(player.is_stop_supported())
        self.assertFalse(player.is_pause_supported())
        self.assertFalse(player.is_next_supported())
        self.assertFalse(player.is_previous_supported())
        self.assertFalse(player.is_repeat_supported())
        self.assertFalse(player.is_shuffle_supported())

    def test_play(self):
        player = NullPlayer()
        self.assertFalse(player.play(MagicMock()))

    def test_jump(self):
        player = NullPlayer()
        player.jump(50)

    def test_resume(self):
        player = NullPlayer()
        player.resume()

    def test_stop(self):
        player = NullPlayer()
        player.stop()

    def test_pause(self):
        player = NullPlayer()
        player.pause()

    def test_next(self):
        player = NullPlayer()
        player.next()

    def test_previous(self):
        player = NullPlayer()
        player.previous()

    def test_get_current_track(self):
        player = NullPlayer()
        track = player.get_current_track()

    def test_repeat(self):
        player = NullPlayer()
        player.repeat(REPEAT_ONE)

    def test_shuffle(self):
        player = NullPlayer()
        player.shuffle(True)

    def test_get_repeat(self):
        player = NullPlayer()
        repeat = player.get_repeat()

        self.assertEqual(repeat, REPEAT_OFF)

    def test_get_shuffle(self):
        player = NullPlayer()
        shuffle = player.get_shuffle()

        self.assertFalse(shuffle)

    def test_is_active(self):
        player = NullPlayer()

        self.assertTrue(player.is_active('wifi', 'cp'))
        self.assertTrue(player.is_active('wifi', 'dlna'))
        self.assertTrue(player.is_active('bt'))
        self.assertTrue(player.is_active(None))
