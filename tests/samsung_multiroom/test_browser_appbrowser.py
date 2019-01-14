import unittest
from unittest.mock import MagicMock
from unittest.mock import call

from samsung_multiroom.browser import AppBrowser
from samsung_multiroom.browser import Item


def _get_browser():
    api = MagicMock()
    api.get_cp_submenu.return_value = [
        {
            '@id': '0',
            'submenuitem_localized': 'Flow',
        },
        {
            '@id': '1',
            'submenuitem_localized': 'Browse',
        },
        {
            '@id': '2',
            'submenuitem_localized': 'Playlist picks',
        },
    ]
    api.set_select_cp_submenu.return_value = [
        {
            '@type': '0',
            'title': 'All',
            'contentid': '0',
        },
        {
            '@type': '0',
            'title': 'Pop',
            'contentid': '1',
        },
        {
            '@type': '0',
            'title': 'Rap/Hip Hop',
            'contentid': '2',
        },
        {
            '@type': '0',
            'title': 'Rock',
            'contentid': '3',
        },
        {
            '@type': '0',
            'title': 'Dance',
            'contentid': '4',
        },
    ]
    api.get_select_radio_list.side_effect = [
        [
            {
                '@type': '0',
                'title': 'Mixes',
                'contentid': '0',
            },
            {
                '@type': '0',
                'title': 'Playlists',
                'contentid': '1',
            },
            {
                '@type': '0',
                'title': 'Albums',
                'contentid': '2',
            },
            {
                '@type': '0',
                'title': 'Artists',
                'contentid': '3',
            },
            {
                '@type': '0',
                'title': 'Editor\'s Picks',
                'contentid': '4',
            },
        ],
        [
            {
                '@type': '3',
                'title': 'Queen',
                'contentid': '0',
                'thumbnail': 'http://api.deezer.com/artist/412/image',
            },
            {
                '@type': '3',
                'title': 'The Beatles',
                'contentid': '1',
                'thumbnail': 'http://api.deezer.com/artist/1/image',
            },
            {
                '@type': '3',
                'title': 'Linking Park',
                'contentid': '2',
                'thumbnail': 'http://api.deezer.com/artist/92/image',
            },
        ],
        [
            {
                '@type': '2',
                'artist': 'Queen',
                'album': None,
                'mediaid': '412',
                'title': 'Queen Mixes',
                'contentid': '0',
                'thumbnail': 'http://api.deezer.com/artist/412/image',
            },
            {
                '@cat': 'Top Tracks',
                '@type': '1',
                '@available': '1',
                '@currentplaying': '1',
                'artist': 'Queen',
                'album': 'A Night At The Opera (2011 Remaster)',
                'mediaid': '9997018',
                'tracklength': '358',
                'title': 'Queen Mixes',
                'contentid': '1',
                'thumbnail': 'http://api.deezer.com/album/915785/image',
            },
            {
                '@cat': 'Top Tracks',
                '@type': '1',
                '@available': '1',
                'artist': 'Queen',
                'album': 'Jazz (2011 Remaster)',
                'mediaid': '12209331',
                'tracklength': '209',
                'title': 'Don\'t Stop Me Now',
                'contentid': '2',
                'thumbnail': 'http://api.deezer.com/album/1121401/image',
            },
            {
                '@cat': 'Albums',
                '@type': '4',
                'artist': None,
                'title': 'Queen Forever',
                'contentid': '6',
                'thumbnail': 'http://api.deezer.com/album/8980335/image',
            },
        ]
    ]

    browser = AppBrowser(api, 3, 'service 3')

    return (browser, api)


class TestAppBrowser(unittest.TestCase):

    def test_get_name(self):
        browser, api = _get_browser()

        name = browser.get_name()

        self.assertEqual(name, 'service 3')

    def test_browse_from_root(self):
        browser, api = _get_browser()

        browser = browser.browse()

        api.get_cp_submenu.assert_called_once()

        self.assertEqual(browser.get_path(), '/')
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, '0')
        self.assertEqual(browser[0].object_type, 'container')
        self.assertEqual(browser[0].name, 'Flow')

    @unittest.mock.patch('inspect.signature')
    def test_browse_second_level(self, signature):
        signature.side_effect = [
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
        ]

        browser, api = _get_browser()

        browser = browser.browse('/Browse')

        api.get_cp_submenu.assert_called_once()
        api.set_select_cp_submenu.assert_called_once_with(content_id='1', start_index=0, list_count=30)

        self.assertEqual(browser.get_path(), '/Browse')
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, '0')
        self.assertEqual(browser[0].object_type, 'container')
        self.assertEqual(browser[0].name, 'All')

    @unittest.mock.patch('inspect.signature')
    def test_browse_full_level(self, signature):
        signature.side_effect = [
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
        ]

        browser, api = _get_browser()

        browser = browser.browse('/Browse/Rock/Artists/Queen/')

        api.get_cp_submenu.assert_called_once()
        api.set_select_cp_submenu.assert_called_once_with(content_id='1', start_index=0, list_count=30)
        api.get_select_radio_list.assert_has_calls([
            call(content_id='3', start_index=0, list_count=30),
            call(content_id='3', start_index=0, list_count=30),
            call(content_id='0', start_index=0, list_count=30),
        ])

        self.assertEqual(browser.get_path(), '/Browse/Rock/Artists/Queen')
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, '0')
        self.assertEqual(browser[0].object_type, 'app_audio')
        self.assertEqual(browser[0].name, 'Queen Mixes')

    @unittest.mock.patch('inspect.signature')
    def test_browse_relative_path(self, signature):
        signature.side_effect = [
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
            type('signature', (object, ), {'parameters': {'content_id': None, 'start_index': None, 'list_count': None}}),
        ]

        browser, api = _get_browser()

        browser = browser.browse('/Browse/Rock').browse('Artists/Queen/')

        api.get_cp_submenu.assert_called_once()
        api.set_select_cp_submenu.assert_called_once_with(content_id='1', start_index=0, list_count=30)
        api.get_select_radio_list.assert_has_calls([
            call(content_id='3', start_index=0, list_count=30),
            call(content_id='3', start_index=0, list_count=30),
            call(content_id='0', start_index=0, list_count=30),
        ])

        self.assertEqual(browser.get_path(), '/Browse/Rock/Artists/Queen')
        self.assertIsInstance(browser[0], Item)
        self.assertEqual(browser[0].object_id, '0')
        self.assertEqual(browser[0].object_type, 'app_audio')
        self.assertEqual(browser[0].name, 'Queen Mixes')
