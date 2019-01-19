"""Abstract media browser and item."""
import abc


class Browser(metaclass=abc.ABCMeta):
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

    @abc.abstractmethod
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

    @abc.abstractmethod
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

    def _get_initial_items(self, folders):
        """
        :returns: initial items to use, for root search return empty list
        """
        if folders[0] is None:
            return []

        return self._get_items()

    def _get_initial_depth(self, folders):
        """
        :returns: depth of the current browse, taking into account relative/absolute browsing
        """
        if folders[0] is None:
            return 0

        return len(path_to_folders(self._path))

    def __getitem__(self, i):
        return self._items[i]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)


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
