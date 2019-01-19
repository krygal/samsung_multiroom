"""Group multiple equalizers together to act on all simultaneously."""
from .equalizer import EqualizerBase


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
