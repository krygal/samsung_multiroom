"""TuneIn service browser."""
from ...api import paginator
from ..browser import Browser
from ..browser import Item
from ..browser import path_to_folders


class TuneInBrowser(Browser):
    """
    TuneIn radio browser.
    """

    def __init__(self, api, path=None, items=None):
        super().__init__(path, items)

        self._api = api

    def get_name(self):
        return 'tunein'

    def browse(self, path=None):
        folders = path_to_folders(path)

        items = self._get_initial_items(folders)

        for folder in folders:
            # locate prepopulated items matching folder
            parent_id = next(iter([i.object_id for i in items if i.name == folder]), None)

            if parent_id is None:
                data_list = paginator(self._api.browse_main, 0, 30)
            else:
                data_list = paginator(self._api.get_select_radio_list, self._api.get_current_radio_list, parent_id, 0,
                                      30)

            items = [self._factory_item(data) for data in data_list]

        return TuneInBrowser(self._api, self._merge_path(path), items)

    def _factory_item(self, data):
        kwargs = {'metadata': {}}

        # mandatory
        if 'contentid' in data:
            kwargs['object_id'] = data['contentid']

        if '@type' in data and data['@type'] == '2':
            kwargs['object_type'] = 'tunein_radio'
        else:
            kwargs['object_type'] = 'container'

        if 'title' in data:
            kwargs['name'] = data['title']

        # metadata
        if 'thumbnail' in data:
            kwargs['metadata']['thumbnail_url'] = data['thumbnail']

        return Item(**kwargs)
