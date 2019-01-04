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
                items = []
                dms_list = paginator(self._api.get_dms_list, 0, 20)

                for dms in dms_list:
                    items.append(dms_to_item(dms))
            else:
                items = []
                if parent_id is None:
                    music_list = paginator(self._api.pc_get_music_list_by_category, device_udn, 0, 20)
                else:
                    music_list = paginator(self._api.pc_get_music_list_by_id, device_udn, parent_id, 0, 20)

                for music_item in music_list:
                    items.append(music_item_to_item(music_item))

        return DlnaBrowser(self._api, self._merge_path(path), items)


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

            # if we don't have device udn we search through devices
            if parent_id is None:
                items = []
                radio_list = paginator(self._api.browse_main, 0, 30)

                for radio_item in radio_list:
                    items.append(radio_to_radio_item(radio_item))
            else:
                items = []
                radio_list = paginator(self._api.get_select_radio_list, self._api.get_current_radio_list, parent_id, 0,
                                       30)

                for radio_item in radio_list:
                    items.append(radio_to_radio_item(radio_item))

        return TuneInBrowser(self._api, self._merge_path(path), items)


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


def dms_to_item(dms):
    """
    :param dms: Dms dict to convert
    :returns: Item instance
    """
    return Item(
        object_id=None,
        object_type='container',
        name=dms['dmsname'],
        metadata={
            'device_udn': dms['dmsid'],
            'device_type': dms['devicetype'],
            'thumbnail_url': dms['thumbnail_JPG_LRG'],
        })


def music_item_to_item(music_item):
    """
    :param music_item: Music item dict to convert
    :returns: Item instance
    """
    if music_item['type'] == 'CONTAINER':
        return Item(
            object_id=music_item['@object_id'],
            object_type='container',
            name=music_item['title'],
            metadata={'device_udn': music_item['device_udn']})
    if music_item['type'] == 'AUDIO':
        (hours, minutes, seconds) = music_item['timelength'].split(':')
        return Item(
            object_id=music_item['@object_id'],
            object_type='dlna_audio',
            name=music_item['title'],
            metadata={
                'device_udn': music_item['device_udn'],
                'artist': music_item['artist'],
                'album': music_item['album'],
                'thumbnail_url': music_item['thumbnail'],
                'duration': int(hours) * 3600 + int(minutes) * 60 + int(float(seconds))
            })

    raise ValueError('Unsupported music item type {0}'.format(music_item['type']))


def radio_to_radio_item(radio):
    """
    :param dms: Radio dict to convert
    :returns: Item instance
    """
    if radio['@type'] == '0':
        return Item(object_id=radio['contentid'], object_type='container', name=radio['title'])
    if radio['@type'] == '2':
        return Item(object_id=radio['contentid'], object_type='tunein_radio', name=radio['title'])

    raise ValueError('Unsupported radio item type {0}'.format(radio['@type']))
