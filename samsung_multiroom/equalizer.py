"""
Control speaker's sound adjustments.
"""
import abc


class EqualizerBase(metaclass=abc.ABCMeta):
    """
    Abstract base class for equalizers.
    """

    @abc.abstractmethod
    def get_presets_names(self):
        """
        :returns: List of preset names
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def set(self, *args):
        """
        Set equalizer values by preset name or list of band values

        :param: Name of the preset to set or list of 7 band values to set
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, name=None):
        """
        Create a new or overwrite existing preset.

        :param name: If empty, current preset will be saved, if provided name exist, that preset will overwrite existing
            one, otherwise a new preset is created with that name. In either case band values used will be ones
            currently set on a speaker e.g. via set() method.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, name):
        """
        Delete preset.

        :param name: Name of a preset to delete
        """
        raise NotImplementedError()


class Equalizer(EqualizerBase):
    """
    Control speaker's sound adjustments.

    Allows adjustments for bands 150, 300, 600, 1.2k, 2.5k, 5.0k, 10.0k, each value must be integer between -6 and 6.
    """

    def __init__(self, api):
        self._api = api

    def get_presets_names(self):
        """
        :returns: List of preset names
        """
        presets = self._api.get_7band_eq_list()

        return [p['presetname'] for p in presets]

    def set(self, *args):
        """
        Set equalizer values by preset name or list of band values

        :param: Name of the preset to set or list of 7 band values to set
        """
        # set by preset name
        if isinstance(args[0], str):
            preset_index = self._get_preset_index_by_name(args[0])
            if not preset_index:
                raise ValueError('Preset {0} does not exists'.format(args[0]))

            self._api.set_7band_eq_mode(preset_index)
        # set band values
        else:
            if not isinstance(args[0], list) or len(args[0]) != 7:
                raise ValueError('Pass all 7 band values as a list')

            if [value for value in args[0] if not isinstance(value, int) or abs(value) > 6]:
                raise ValueError('Band values must be integers between -6 and 6')

            preset_index = self._get_current_preset()['id']
            self._api.set_7band_eq_value(preset_index, args[0])

    def save(self, name=None):
        """
        Create a new or overwrite existing preset.

        :param name: If empty, current preset will be saved, if provided name exist, that preset will overwrite existing
            one, otherwise a new preset is created with that name. In either case band values used will be ones
            currently set on a speaker e.g. via set() method.
        """
        current_preset = self._get_current_preset()

        # overwrite current one
        if name is None:
            self._api.reset_7band_eq_value(current_preset['id'], current_preset['band_values'])
        else:
            preset_index = self._get_preset_index_by_name(name)

            # overwrite preset with the same name
            if preset_index:
                self._api.reset_7band_eq_value(preset_index, current_preset['band_values'])
            # create a new preset
            else:
                presets = self._api.get_7band_eq_list()
                presets_ids = [int(p['presetindex']) for p in presets]

                self._api.add_custom_eq_mode(max(presets_ids) + 1, name)

    def delete(self, name):
        """
        Delete preset.

        :param name: Name of a preset to delete
        """
        preset_index = self._get_preset_index_by_name(name)

        if not preset_index:
            raise ValueError('Preset {0} does not exists'.format(name))

        self._api.del_custom_eq_mode(preset_index)

    def _get_preset_index_by_name(self, name):
        presets = self._api.get_7band_eq_list()
        matching_presets = [int(p['presetindex']) for p in presets if p['presetname'] == name]

        if matching_presets:
            return matching_presets[0]

        return None

    def _get_current_preset(self):
        preset = self._api.get_current_eq_mode()

        return {
            'id': int(preset['presetindex']),
            'name': preset['presetname'],
            'band_values': [int(preset['eqvalue' + str(i)]) for i in range(1, 8)]
        }


class EqualizerGroup(EqualizerBase):
    """
    Group multiple equalizers together to act on all simultaneously.
    """

    def __init__(self, equalizers):
        """
        :param equalizers: List of EqualizerBase implementations
        """
        self._equalizers = equalizers

    @property
    def equalizers(self):
        """
        :returns: List of equalizers
        """
        return self._equalizers

    def get_presets_names(self):
        """
        :returns: List of preset names shared by all equalizers.
        """
        presets_names = self._equalizers[0].get_presets_names()

        for equalizer in self._equalizers[1:]:
            eq_presets_names = equalizer.get_presets_names()
            presets_names = [p for p in presets_names if p in eq_presets_names]

        return presets_names

    def set(self, *args):
        """
        Set equalizer values by preset name or list of band values for all equalizers.

        :param: Name of the preset to set or list of 7 band values to set
        """
        for equalizer in self._equalizers:
            equalizer.set(*args)

    def save(self, name=None):
        """
        Create a new or overwrite existing preset for all equalizers.

        :param name: If empty, current preset will be saved, if provided name exist, that preset will overwrite existing
            one, otherwise a new preset is created with that name. In either case band values used will be ones
            currently set on a speaker e.g. via set() method.
        """
        for equalizer in self._equalizers:
            equalizer.save(name)

    def delete(self, name):
        """
        Delete preset from all equalizers.

        :param name: Name of a preset to delete
        """
        for equalizer in self._equalizers:
            equalizer.delete(name)
