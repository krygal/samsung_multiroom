"""Generic music streaming app service browser."""
from ...api import paginator
from ..browser import Browser
from ..browser import Item
from ..browser import path_to_folders


class AppBrowser(Browser):
    """
    Generic music streaming app service browser.
    """

    def __init__(self, api, app_id, app_name, path=None, items=None):
        super().__init__(path, items)

        self._api = api
        self._id = app_id
        self._name = app_name

    def get_name(self):
        return self._name

    def browse(self, path=None):
        folders = path_to_folders(path)

        items = self._get_initial_items(folders)
        depth = self._get_initial_depth(folders)

        for folder in folders:
            depth += 1

            # locate prepopulated items matching folder
            parent_id = next(iter([i.object_id for i in items if i.name == folder]), None)

            if parent_id is None:
                data_list = self._api.get_cp_submenu()
            elif depth <= 2:
                data_list = paginator(self._api.set_select_cp_submenu, parent_id, 0, 30)
            else:
                data_list = paginator(self._api.get_select_radio_list, self._api.get_current_radio_list, parent_id, 0,
                                      30)

            items = [self._factory_item(data) for data in data_list]

        return AppBrowser(self._api, self._id, self._name, self._merge_path(path), items)

    def _factory_item(self, data):
        kwargs = {'metadata': {}}

        # mandatory
        if '@id' in data:
            kwargs['object_id'] = data['@id']
        if 'contentid' in data:
            kwargs['object_id'] = data['contentid']

        if '@type' in data and data['@type'] in ('1', '2'):
            kwargs['object_type'] = 'app_audio'
        else:
            kwargs['object_type'] = 'container'

        if 'submenuitem_localized' in data:
            kwargs['name'] = data['submenuitem_localized']
        if 'title' in data:
            kwargs['name'] = data['title']

        # metadata
        if 'artist' in data:
            kwargs['metadata']['artist'] = data['artist']
        if 'album' in data:
            kwargs['metadata']['album'] = data['album']
        if 'tracklength' in data:
            kwargs['metadata']['duration'] = int(data['tracklength'])
        if 'thumbnail' in data:
            kwargs['metadata']['thumbnail_url'] = data['thumbnail']

        return Item(**kwargs)
