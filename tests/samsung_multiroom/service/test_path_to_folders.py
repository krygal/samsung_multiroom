import unittest

from samsung_multiroom.service import path_to_folders


class TestPathToFolders(unittest.TestCase):

    def test_path_to_folders(self):
        self.assertEqual(path_to_folders(None), [None])
        self.assertEqual(path_to_folders(''), [None])
        self.assertEqual(path_to_folders('/'), [None])
        self.assertEqual(path_to_folders('/Folder1'), [None, 'Folder1'])
        self.assertEqual(path_to_folders('/Folder1/'), [None, 'Folder1'])
        self.assertEqual(path_to_folders('/Folder1/Folder2/Folder3/'), [None, 'Folder1', 'Folder2', 'Folder3'])
