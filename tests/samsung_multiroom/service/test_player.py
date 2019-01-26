import unittest

from samsung_multiroom.service import Player
from samsung_multiroom.service.player import unsupported


class FakePlayer(Player):

    def play(self, playlist):
        """Fake."""
        return False

    def jump(self, time):
        """Fake."""

    def resume(self):
        """Fake."""

    def stop(self):
        """Fake."""

    def pause(self):
        """Fake."""

    def next(self):
        """Fake."""

    def previous(self):
        """Fake."""

    @unsupported
    def repeat(self, mode):
        """Fake."""

    def shuffle(self, enabled):
        """Fake."""

    def get_repeat(self):
        """Fake."""
        return REPEAT_OFF

    def get_shuffle(self):
        """Fake."""
        return False

    def get_current_track(self):
        """Fake."""
        return None

    def is_active(self, function, submode=None):
        """Fake."""
        return True



class TestPlayer(unittest.TestCase):

    def test_unsupported(self):
        player = FakePlayer()
        self.assertTrue(player.is_play_supported())
        self.assertFalse(player.is_repeat_supported())

        self.assertTrue(hasattr(player, 'is_play_supported'))
        self.assertTrue(hasattr(player, 'is_repeat_supported'))
        self.assertFalse(hasattr(player, 'is_nonsense_supported'))
