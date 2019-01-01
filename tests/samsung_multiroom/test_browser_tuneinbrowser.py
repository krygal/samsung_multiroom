import unittest
from unittest.mock import MagicMock
from unittest.mock import call

from samsung_multiroom.browser import ContainerItem
from samsung_multiroom.browser import TuneInBrowser
from samsung_multiroom.browser import TuneInRadioItem


def browser_main_return_value():
    return [
        {
            '@type': '0',
            'title': 'Favorites',
            'contentid': '0',
        },
        {
            '@type': '0',
            'title': 'Local Radio',
            'contentid': '1',
        },
        {
            '@type': '0',
            'title': 'Recents',
            'contentid': '2',
        },
        {
            '@type': '0',
            'title': 'Trending',
            'contentid': '3',
        },
        {
            '@type': '0',
            'title': 'By Language',
            'contentid': '10',
        }
    ]


def get_select_radio_list_side_effect(content_id, start_index, list_count):
    if content_id == '10':
        return [
            {
                '@type': '0',
                'title': 'Arabic',
                'contentid': '4',
            },
            {
                '@type': '0',
                'title': 'English',
                'contentid': '24',
            },
            {
                '@type': '0',
                'title': 'Finnish',
                'contentid': '28',
            },
            {
                '@type': '0',
                'title': 'French',
                'contentid': '29',
            },
        ]
    if content_id == '24':
        return [
            {
                '@type': '0',
                'title': 'Music',
                'contentid': '0',
            },
            {
                '@type': '0',
                'title': 'Talk',
                'contentid': '1',
            },
        ]
    if content_id == '0':
        return [
            {
                '@type': '2',
                'thumbnail': 'http://cdn-profiles.tunein.com/s297990/images/logot.png',
                'description': 'MSNBC Live with Velshi & Ruhle',
                'mediaid': 's297990',
                'title': 'MSNBC',
                'contentid': '0',
            },
            {
                '@type': '2',
                'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s24940t.png',
                'description': 'Amazing music. Played by an amazing line up.',
                'mediaid': 's24940',
                'title': 'BBC1',
                'contentid': '1',
            }
        ]


class TestTuneInBrowser(unittest.TestCase):

    def test_list_from_root(self):
        api = MagicMock()
        api.browse_main.return_value = browser_main_return_value()

        browser = TuneInBrowser(api)
        browser = browser.list()

        api.browse_main.assert_called_once_with(0, 30)

        self.assertEqual(browser.get_path(), '/')
        self.assertEqual(len(browser), 5)
        self.assertIsInstance(browser[0], ContainerItem)
        self.assertEqual(browser[0].name, 'Favorites')
        self.assertEqual(browser[0].object_id, '0')

    def test_list_full_level(self):
        api = MagicMock()
        api.browse_main.return_value = browser_main_return_value()
        api.get_select_radio_list.side_effect = get_select_radio_list_side_effect

        browser = TuneInBrowser(api)
        browser = browser.list('/By Language/English/Music')

        api.browse_main.assert_called_once_with(0, 30)
        api.get_select_radio_list.assert_has_calls([
            call('10', 0, 30),
            call('24', 0, 30),
            call('0', 0, 30),
        ])

        self.assertEqual(browser.get_path(), '/By Language/English/Music')
        self.assertEqual(len(browser), 2)
        self.assertIsInstance(browser[0], TuneInRadioItem)
        self.assertEqual(browser[0].name, 'MSNBC')
        self.assertEqual(browser[0].object_id, '0')

    def test_list_relative(self):
        api = MagicMock()
        api.browse_main.return_value = browser_main_return_value()
        api.get_select_radio_list.side_effect = get_select_radio_list_side_effect

        browser = TuneInBrowser(api)
        browser = browser.list('/By Language/English').list('Music')

        api.browse_main.assert_called_once_with(0, 30)
        api.get_select_radio_list.assert_has_calls([
            call('10', 0, 30),
            call('24', 0, 30),
            call('0', 0, 30),
        ])

        self.assertEqual(browser.get_path(), '/By Language/English/Music')
        self.assertEqual(len(browser), 2)
        self.assertIsInstance(browser[0], TuneInRadioItem)
        self.assertEqual(browser[0].name, 'MSNBC')
        self.assertEqual(browser[0].object_id, '0')
