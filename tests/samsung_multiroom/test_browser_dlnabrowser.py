import unittest
from unittest.mock import MagicMock
from unittest.mock import call

from samsung_multiroom.browser import DlnaBrowser
from samsung_multiroom.browser import Item
from samsung_multiroom.browser import path_to_folders


def get_dms_list_return_value():
    return [
        {
            '@device_id': '0',
            'dmsid': 'uuid:00113249-398f-0011-8f39-8f3949321100',
            'dmsname': 'NAS',
            'devicetype': 'network',
            'thumbnail_PNG_LRG': 'http://192.168.1.111:50001/tmp_icon/dmsicon120.png',
            'thumbnail_JPG_LRG': 'http://192.168.1.111:50001/tmp_icon/dmsicon120.jpg',
            'thumbnail_PNG_SM': 'http://192.168.1.111:50001/tmp_icon/dmsicon48.png',
            'thumbnail_JPG_SM': 'http://192.168.1.111:50001/tmp_icon/dmsicon48.jpg',
        },
    ]

def pc_get_music_list_by_category_return_value():
    return [
        {
            '@object_id': '21',
            'type': 'CONTAINER',
            'playindex': '-1',
            'name': None,
            'title': 'Music',
            'artist': None,
            'album': None,
            'thumbnail': None,
            'timelength': None,
            'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
        },
        {
            '@object_id': '37',
            'type': 'CONTAINER',
            'playindex': '-1',
            'name': None,
            'title': 'Photo',
            'artist': None,
            'album': None,
            'thumbnail': None,
            'timelength': None,
            'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
        },
        {
            '@object_id': '44',
            'type': 'CONTAINER',
            'playindex': '-1',
            'name': None,
            'title': 'Video',
            'artist': None,
            'album': None,
            'thumbnail': None,
            'timelength': None,
            'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
        },
    ]

def pc_get_music_list_by_id_side_effect(device_udn, parent_id, start_index, list_count):
    if parent_id == '21':
        return [
            {
                '@object_id': '22',
                'type': 'CONTAINER',
                'playindex': '-1',
                'name': None,
                'title': 'By Folder',
                'artist': None,
                'album': None,
                'thumbnail': None,
                'timelength': None,
                'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
            },
        ]
    if parent_id == '22':
        return [
            {
                '@object_id': '22$@52941',
                'type': 'AUDIO',
                'playindex': '0',
                'name': 'La femme d\'argent.mp3',
                'title': 'La femme d\'argent',
                'artist': 'Air',
                'album': 'Moon Safari',
                'thumbnail': 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52941.jpg',
                'timelength': '0:07:11.000',
                'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
            },
            {
                '@object_id': '22$@52942',
                'type': 'AUDIO',
                'playindex': '0',
                'name': 'Sexy boy.mp3',
                'title': 'Sexy boy',
                'artist': 'Air',
                'album': 'Moon Safari',
                'thumbnail': 'http://192.168.1.111:50002/transcoder/jpegtnscaler.cgi/folderart/52942.jpg',
                'timelength': '0:04:58.000',
                'device_udn': 'uuid:00113249-398f-0011-8f39-8f3949321100',
            },
        ]


class TestDlnaBrowser(unittest.TestCase):

    def test_path_to_folders(self):
        self.assertEqual(path_to_folders(None), [None])
        self.assertEqual(path_to_folders(''), [None])
        self.assertEqual(path_to_folders('/'), [None])
        self.assertEqual(path_to_folders('/Folder1'), [None, 'Folder1'])
        self.assertEqual(path_to_folders('/Folder1/'), [None, 'Folder1'])
        self.assertEqual(path_to_folders('/Folder1/Folder2/Folder3/'), [None, 'Folder1', 'Folder2', 'Folder3'])

    @unittest.mock.patch('inspect.signature')
    def test_browse_from_root(self, signature):
        signature.side_effect = [
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
        ]

        api = MagicMock()
        api.get_dms_list.return_value = get_dms_list_return_value()

        browser = DlnaBrowser(api)
        browser = browser.browse()

        api.get_dms_list.assert_called_once_with(start_index=0, list_count=20)

        self.assertEqual(browser.get_path(), '/')
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, None)
        self.assertEqual(browser[0].object_type, 'container')
        self.assertEqual(browser[0].name, 'NAS')
        self.assertEqual(browser[0].device_udn, 'uuid:00113249-398f-0011-8f39-8f3949321100')

    @unittest.mock.patch('inspect.signature')
    def test_browse_second_level(self, signature):
        signature.side_effect = [
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'start_index': None, 'list_count': None}}),
        ]

        api = MagicMock()
        api.get_dms_list.return_value = get_dms_list_return_value()
        api.pc_get_music_list_by_category.return_value = pc_get_music_list_by_category_return_value()

        browser = DlnaBrowser(api)
        browser = browser.browse('/NAS/')

        api.get_dms_list.assert_called_once_with(start_index=0, list_count=20)
        api.pc_get_music_list_by_category.assert_called_once_with(device_udn='uuid:00113249-398f-0011-8f39-8f3949321100', start_index=0, list_count=20)

        self.assertEqual(browser.get_path(), '/NAS')
        self.assertEqual(len(browser), 3)
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, '21')
        self.assertEqual(browser[0].object_type, 'container')
        self.assertEqual(browser[0].name, 'Music')
        self.assertEqual(browser[0].device_udn, 'uuid:00113249-398f-0011-8f39-8f3949321100')

    @unittest.mock.patch('inspect.signature')
    def test_browse_full_level(self, signature):
        signature.side_effect = [
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
        ]

        api = MagicMock()
        api.get_dms_list.return_value = get_dms_list_return_value()
        api.pc_get_music_list_by_category.return_value = pc_get_music_list_by_category_return_value()
        api.pc_get_music_list_by_id.side_effect = pc_get_music_list_by_id_side_effect

        browser = DlnaBrowser(api)
        browser = browser.browse('/NAS/Music/By Folder')

        api.get_dms_list.assert_called_once_with(start_index=0, list_count=20)
        api.pc_get_music_list_by_category.assert_called_once_with(device_udn='uuid:00113249-398f-0011-8f39-8f3949321100', start_index=0, list_count=20)
        api.pc_get_music_list_by_id.assert_has_calls([
            call(device_udn='uuid:00113249-398f-0011-8f39-8f3949321100', parent_id='21', start_index=0, list_count=20),
            call(device_udn='uuid:00113249-398f-0011-8f39-8f3949321100', parent_id='22', start_index=0, list_count=20),
        ])

        self.assertEqual(browser.get_path(), '/NAS/Music/By Folder')
        self.assertEqual(len(browser), 2)
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, '22$@52941')
        self.assertEqual(browser[0].object_type, 'dlna_audio')
        self.assertEqual(browser[0].name, 'La femme d\'argent')
        self.assertEqual(browser[0].device_udn, 'uuid:00113249-398f-0011-8f39-8f3949321100')

    @unittest.mock.patch('inspect.signature')
    def test_browse_relative_path(self, signature):
        signature.side_effect = [
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'device_udn': None, 'parent_id':None, 'start_index': None, 'list_count': None}}),
        ]

        api = MagicMock()
        api.get_dms_list.return_value = get_dms_list_return_value()
        api.pc_get_music_list_by_category.return_value = pc_get_music_list_by_category_return_value()
        api.pc_get_music_list_by_id.side_effect = pc_get_music_list_by_id_side_effect

        browser = DlnaBrowser(api)
        browser = browser.browse('/NAS/Music/').browse('By Folder')

        api.get_dms_list.assert_called_once_with(start_index=0, list_count=20)
        api.pc_get_music_list_by_category.assert_called_once_with(device_udn='uuid:00113249-398f-0011-8f39-8f3949321100', start_index=0, list_count=20)
        api.pc_get_music_list_by_id.assert_has_calls([
            call(device_udn='uuid:00113249-398f-0011-8f39-8f3949321100', parent_id='21', start_index=0, list_count=20),
            call(device_udn='uuid:00113249-398f-0011-8f39-8f3949321100', parent_id='22', start_index=0, list_count=20),
        ])

        self.assertEqual(browser.get_path(), '/NAS/Music/By Folder')
        self.assertEqual(len(browser), 2)
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, '22$@52941')
        self.assertEqual(browser[0].object_type, 'dlna_audio')
        self.assertEqual(browser[0].name, 'La femme d\'argent')
        self.assertEqual(browser[0].device_udn, 'uuid:00113249-398f-0011-8f39-8f3949321100')
