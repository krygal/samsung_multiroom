import unittest
from unittest.mock import MagicMock

from samsung_multiroom.player import NullPlayer


class TestNullPlayer(unittest.TestCase):

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

    def test_is_supported(self):
        player = NullPlayer()

        self.assertTrue(player.is_supported('wifi', 'cp'))
        self.assertTrue(player.is_supported('wifi', 'dlna'))
        self.assertTrue(player.is_supported('bt'))
        self.assertTrue(player.is_supported(None))
