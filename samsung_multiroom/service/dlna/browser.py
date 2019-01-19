"""DLNA service browser."""
from ...api import paginator
from ..browser import Browser
from ..browser import Item
from ..browser import path_to_folders


class DlnaBrowser(Browser):
    """
    DLNA DMS device browser.
    """

    def __init__(self, api, path=None, items=None):
        super().__init__(path, items)

        self._api = api

    def get_name(self):
        return 'dlna'

    def browse(self, path=None):
        folders = path_to_folders(path)

        items = self._get_initial_items(folders)

        for folder in folders:
            # locate prepopulated items matching folder
            device_udn, parent_id = next(
                iter([(i.device_udn, i.object_id) for i in items if i.name == folder]), (None, None))

            # if we don't have device udn we search through devices
            if device_udn is None:
                data_list = paginator(self._api.get_dms_list, 0, 20)
            elif parent_id is None:
                data_list = paginator(self._api.pc_get_music_list_by_category, device_udn, 0, 20)
            else:
                data_list = paginator(self._api.pc_get_music_list_by_id, device_udn, parent_id, 0, 20)

            items = [self._factory_item(data) for data in data_list]

        return DlnaBrowser(self._api, self._merge_path(path), items)

    def _factory_item(self, data):
        kwargs = {'metadata': {}}

        # mandatory
        if 'dmsid' in data:
            kwargs['object_id'] = None
        if '@object_id' in data:
            kwargs['object_id'] = data['@object_id']

        if 'type' in data and data['type'] == 'AUDIO':
            kwargs['object_type'] = 'dlna_audio'
        else:
            kwargs['object_type'] = 'container'

        if 'dmsname' in data:
            kwargs['name'] = data['dmsname']
        if 'title' in data:
            kwargs['name'] = data['title']

        # metadata
        if 'artist' in data:
            kwargs['metadata']['artist'] = data['artist']
        if 'album' in data:
            kwargs['metadata']['album'] = data['album']
        if 'timelength' in data and data['timelength']:
            (hours, minutes, seconds) = data['timelength'].split(':')
            kwargs['metadata']['duration'] = int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
        if 'thumbnail' in data:
            kwargs['metadata']['thumbnail_url'] = data['thumbnail']
        if 'thumbnail_JPG_LRG' in data:
            kwargs['metadata']['thumbnail_url'] = data['thumbnail_JPG_LRG']
        if 'devicetype' in data:
            kwargs['metadata']['device_type'] = data['devicetype']
        if 'dmsid' in data:
            kwargs['metadata']['device_udn'] = data['dmsid']
        if 'device_udn' in data:
            kwargs['metadata']['device_udn'] = data['device_udn']

        return Item(**kwargs)
