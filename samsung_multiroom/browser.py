"""Browse media sources."""


ITEM_TYPE_DEVICE = 'device'
ITEM_TYPE_CONTAINER = 'container'
ITEM_TYPE_AUDIO = 'audio'
ITEM_TYPE_OTHER = 'other'


class Browser:
    """
    Abstract media browser.

    Implementations should be immutable.
    """

    def __init__(self, items=None):
        self._items = items.copy() if items else []

    def list(self, path=None):
        """
        List items based on path.

        :param path: Forward slash separated string of folders e.g. /NAS/Music/By Folder/Air/Moon Safari/CD1
        :returns: Browser instance with listed items
        """
        raise NotImplementedError()

    def _get_items(self):
        return self._items

    def __getitem__(self, i):
        return self._items[i]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return self._items.copy()


class Item:
    """
    Immutable browser item.
    """
    def __init__(self, device_udn, object_id, name, metadata=None):
        self._device_udn = device_udn
        self._object_id = object_id
        self._name = name
        self._metadata = metadata or {}

    @property
    def device_udn(self):
        """
        :returns: Unique Device Name
        """
        return self._device_udn

    @property
    def object_id(self):
        """
        :returns: Object id
        """
        return self._object_id

    @property
    def name(self):
        """
        :returns: Item name
        """
        return self._name

    @property
    def metadata(self):
        """
        :returns: Item metadata specific to item type
        """
        return self._metadata


class ContainerItem(Item):
    """
    Container item.
    """


class AudioItem(Item):
    """
    Audio item.
    """


class RadioItem(Item):
    """
    Radio item.
    """


class DlnaBrowser(Browser):
    """
    DLNA DMA device browser.
    """

    def __init__(self, api, items=None):
        super().__init__(items)

        self._api = api

    def list(self, path=None):
        path = unify_path(path)

        device_udn = None
        parent_id = None

        # from root
        if path[0] is None:
            items = []
        else:
            items = self._get_items()

        for folder in path:
            # locate prepopulated items matching folder
            for item in items:
                if item.name == folder:
                    device_udn = item.device_udn
                    parent_id = item.object_id
                    break

            # if we don't have device udn we search through devices
            if device_udn is None:
                items = []
                dms_list = self._api.get_dms_list(0, 20)

                for dms in dms_list:
                    items.append(dms_to_item(dms))
            else:
                items = []
                if parent_id is None:
                    music_list = self._api.pc_get_music_list_by_category(device_udn, 0, 20)
                else:
                    music_list = self._api.pc_get_music_list_by_id(device_udn, parent_id, 0, 20)

                for music_item in music_list:
                    items.append(music_item_to_item(music_item))

        return DlnaBrowser(self._api, items)


class TuneInBrowser(Browser):
    """
    TuneIn radio browser.
    """

    def __init__(self, api, items=None):
        super().__init__(items)

        self._api = api

    def list(self, path=None):
        path = unify_path(path)

        parent_id = None

        # from root
        if path[0] is None:
            items = []
        else:
            items = self._get_items()

        for folder in path:
            # locate prepopulated items matching folder
            for item in items:
                if item.name == folder:
                    parent_id = item.object_id
                    break

            # if we don't have device udn we search through devices
            if parent_id is None:
                items = []
                radio_list = self._api.browse_main(0, 30)

                for radio_item in radio_list:
                    items.append(radio_to_radio_item(radio_item))
            else:
                items = []
                radio_list = self._api.get_select_radio_list(parent_id, 0, 30)

                for radio_item in radio_list:
                    items.append(radio_to_radio_item(radio_item))

        return TuneInBrowser(self._api, items)


def unify_path(path):
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


def dms_to_item(dms):
    """
    :param dms: Dms dict to convert
    :returns: Item instance
    """
    return Item(
        device_udn=dms['dmsid'],
        object_id=None,
        name=dms['dmsname']
    )


def radio_to_radio_item(radio):
    """
    :param dms: Radio dict to convert
    :returns: Item instance
    """
    if radio['@type'] == '0':
        return ContainerItem(
            device_udn=None,
            object_id=radio['contentid'],
            name=radio['title']
        )
    if radio['@type'] == '2':
        return RadioItem(
            device_udn=None,
            object_id=radio['contentid'],
            name=radio['title']
        )

    raise ValueError('Unsupported radio item type {0}'.format(radio['@type']))


def music_item_to_item(music_item):
    """
    :param music_item: Music item dict to convert
    :returns: Item instance
    """
    item_type = Item
    if music_item['type'] == 'CONTAINER':
        item_type = ContainerItem
    if music_item['type'] == 'AUDIO':
        item_type = AudioItem

    return item_type(
        device_udn=music_item['device_udn'],
        object_id=music_item['@object_id'],
        name=music_item['title']
    )
