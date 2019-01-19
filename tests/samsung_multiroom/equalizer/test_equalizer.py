import unittest
from unittest.mock import MagicMock

from samsung_multiroom.equalizer import Equalizer


def get_equalizer():
    api = MagicMock()
    api.get_7band_eq_list.return_value = [
        {
            '@index': '0',
            'presetindex': '0',
            'presetname': 'Pop',
        },
        {
            '@index': '1',
            'presetindex': '1',
            'presetname': 'Rock',
        },
        {
            '@index': '2',
            'presetindex': '2',
            'presetname': 'Custom 1',
        }
    ]
    api.get_current_eq_mode.return_value = {
        'presetindex': '1',
        'presetname': 'Rock',
        'eqvalue1': '4',
        'eqvalue2': '2',
        'eqvalue3': '0',
        'eqvalue4': '0',
        'eqvalue5': '1',
        'eqvalue6': '2',
        'eqvalue7': '1',
    }

    equalizer = Equalizer(api)

    return (equalizer, api)


class TestEqualizer(unittest.TestCase):

    def test_get_presets_names(self):
        equalizer, api = get_equalizer()

        presets_names = equalizer.get_presets_names()

        self.assertEqual(presets_names, ['Pop', 'Rock', 'Custom 1'])

    def test_set_by_preset_name(self):
        equalizer, api = get_equalizer()

        equalizer.set('Rock')

        api.set_7band_eq_mode.assert_called_once_with(1)

    def test_set_by_preset_name_exception(self):
        equalizer, api = get_equalizer()

        self.assertRaises(ValueError, equalizer.set, 'Invalid preset')

        api.set_7band_eq_mode.assert_not_called()

    def test_set_by_bands(self):
        equalizer, api = get_equalizer()

        equalizer.set([1,2,3,4,5,6,-6])

        api.set_7band_eq_value.assert_called_once_with(1, [1,2,3,4,5,6,-6])

    def test_set_by_bands_incorrect(self):
        equalizer, api = get_equalizer()

        self.assertRaises(ValueError, equalizer.set, 1,2,3,4,5,6,6)
        self.assertRaises(ValueError, equalizer.set, [1,2,3])
        self.assertRaises(ValueError, equalizer.set, [1,2,3,4,5,6,6,6,6])
        self.assertRaises(ValueError, equalizer.set, [1,2,3,4,5,6,7])
        self.assertRaises(ValueError, equalizer.set, [1,2,3,4,5,6,-7])
        self.assertRaises(ValueError, equalizer.set, [1,2,3,4,5,6,'Hello there'])

        api.set_7band_eq_value.assert_not_called()

    def test_save_create_new(self):
        equalizer, api = get_equalizer()

        equalizer.save('My new preset')

        api.add_custom_eq_mode.assert_called_once_with(3, 'My new preset')

    def test_save_overwrite_existing(self):
        equalizer, api = get_equalizer()

        equalizer.save('Custom 1')

        api.reset_7band_eq_value.assert_called_once_with(2, [4,2,0,0,1,2,1])

    def test_save_overwrite_current(self):
        equalizer, api = get_equalizer()

        equalizer.save()

        api.reset_7band_eq_value.assert_called_once_with(1, [4,2,0,0,1,2,1])

    def test_delete(self):
        equalizer, api = get_equalizer()

        equalizer.delete('Custom 1')

        api.del_custom_eq_mode.assert_called_once_with(2)

    def test_delete_missing(self):
        equalizer, api = get_equalizer()

        self.assertRaises(ValueError, equalizer.delete, 'Invalid preset')

        api.del_custom_eq_mode.assert_not_called()
