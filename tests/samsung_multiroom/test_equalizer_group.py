import unittest
from unittest.mock import MagicMock

from samsung_multiroom.equalizer import EqualizerGroup


def _get_equalizer_group():
    equalizers = [
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]

    equalizer_group = EqualizerGroup(equalizers)

    return (equalizer_group, equalizers)


class TestEqualizerGroup(unittest.TestCase):

    def test_get_presets_names_returns_shared(self):
        equalizer_group, equalizers = _get_equalizer_group()

        equalizers[0].get_presets_names.return_value = ['None', 'Pop', 'Jazz', 'Classic', 'Custom 1', 'Custom 2']
        equalizers[1].get_presets_names.return_value = ['None', 'Pop', 'Jazz', 'Classic', 'Custom 2', 'Custom 3']
        equalizers[2].get_presets_names.return_value = ['None', 'Pop', 'Jazz', 'Classic', 'Custom 2', 'Custom 4']

        presets_names = equalizer_group.get_presets_names()

        self.assertEqual(presets_names, ['None', 'Pop', 'Jazz', 'Classic', 'Custom 2'])

    def test_set_sets_all_equalizers(self):
        equalizer_group, equalizers = _get_equalizer_group()

        equalizer_group.set('Jazz')

        equalizers[0].set.assert_called_once_with('Jazz')
        equalizers[1].set.assert_called_once_with('Jazz')
        equalizers[2].set.assert_called_once_with('Jazz')

    def test_save_saves_all_equalizers(self):
        equalizer_group, equalizers = _get_equalizer_group()

        equalizer_group.save('Custom 7')

        equalizers[0].save.assert_called_once_with('Custom 7')
        equalizers[1].save.assert_called_once_with('Custom 7')
        equalizers[2].save.assert_called_once_with('Custom 7')

    def test_delete_deletes_all_equalizers(self):
        equalizer_group, equalizers = _get_equalizer_group()

        equalizer_group.delete('Custom 7')

        equalizers[0].delete.assert_called_once_with('Custom 7')
        equalizers[1].delete.assert_called_once_with('Custom 7')
        equalizers[2].delete.assert_called_once_with('Custom 7')
