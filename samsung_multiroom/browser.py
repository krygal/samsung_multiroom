"""Browse media sources."""
from .api import paginator


class Browser:
    """
    Abstract media browser.

    Implementations should be immutable.
    """

    def __init__(self, path=None, items=None):
        """
        :param path: Path used to list items
        :param items: Items listed
        """
        self._path = path
        self._items = items.copy() if items else []

    def get_name(self):
        """
        :returns: Name of the browser
        """
        raise NotImplementedError()

    def get_path(self):
        """
        :returns: Path used to list items
        """
        return self._path

    def browse(self, path=None):
        """
        List items based on path.

        :param path: Forward slash separated string of folders e.g. /NAS/Music/By Folder/Air/Moon Safari/CD1
        :returns: Browser instance with listed items
        """
        raise NotImplementedError()

    def _merge_path(self, new_path):
        folders = path_to_folders(new_path)

        if folders[0] is not None:
            folders = path_to_folders(self.get_path()) + folders

        return folders_to_path(folders)

    def _get_items(self):
        return self._items

    def __getitem__(self, i):
        return self._items[i]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)


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

        device_udn = None
        parent_id = None

        # from root
        if folders[0] is None:
            items = []
        else:
            items = self._get_items()

        for folder in folders:
            # locate prepopulated items matching folder
            for item in items:
                if item.name == folder:
                    device_udn = item.device_udn
                    parent_id = item.object_id
                    break

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

        parent_id = None

        # from root
        if folders[0] is None:
            items = []
        else:
            items = self._get_items()

        for folder in folders:
            # locate prepopulated items matching folder
            for item in items:
                if item.name == folder:
                    parent_id = item.object_id
                    break

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

        parent_id = None

        # from root
        if folders[0] is None:
            items = []
            depth = 0
        else:
            items = self._get_items()
            depth = len(path_to_folders(self._path))

        for folder in folders:
            depth += 1

            # locate prepopulated items matching folder
            for item in items:
                if item.name == folder:
                    parent_id = item.object_id
                    break

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


class Item:
    """
    Immutable browser item.
    """

    def __init__(self, object_id, object_type, name, metadata=None):
        self._object_id = object_id
        self._object_type = object_type
        self._name = name
        self._metadata = metadata or {}

    @property
    def object_id(self):
        """
        :returns: Object id
        """
        return self._object_id

    @property
    def object_type(self):
        """
        :returns: Object type
        """
        return self._object_type

    @property
    def name(self):
        """
        :returns: Item name
        """
        return self._name

    @property
    def title(self):
        """
        :returns: Item title, equivallent of name
        """
        if 'title' in self._metadata:
            return self._metadata['title']

        return self.name

    @property
    def metadata(self):
        """
        :returns: Item metadata specific to item type
        """
        return self._metadata

    def __getattr__(self, name):
        """
        Look up name in metadata.

        :returns: Metadata value
        """
        if name in self._metadata:
            return self._metadata[name]

        return None


def path_to_folders(path):
    """
    Convert path to a standarised list of folder.

    If path is prepended with /, first element on the list will be special folder None denoting root.

    :param path: None or path string with folders '/' separated, e.g. /NAS/Music/By Folder/folder1/folder2
    :returns: List of folders e.g. [None, 'NAS', 'Music', 'By Folder', 'folder1', 'folder2']
    """
    if path in [None, '', '/']:
        path = '/'

    is_from_root = (path[0] == '/')

    path = path.strip(' /').split('/')
    path = [p for p in path if p != '']

    if is_from_root:
        path.insert(0, None)

    return path


def folders_to_path(folders):
    """
    Convert list of folders to a path.

    :param folders: List of folders, None denotes a root folder e.g. [None, 'NAS', 'Music', 'By Folder', 'folder1']
    :returns: path string e.g. /NAS/Music/By Folder/folder1
    """
    if not folders:
        return '/'

    if folders[0] is None:
        folders[0] = ''

    return '/'.join(folders) or '/'
