import unittest
from unittest.mock import MagicMock

from samsung_multiroom.browser import AppBrowser
from samsung_multiroom.service import AppService


def _get_service():
    api = MagicMock()

    service = AppService(api, 12, 'Service 2')

    return (service, api)


class TestAppService(unittest.TestCase):

    def test_name(self):
        service, api = _get_service()

        self.assertEqual(service.name, 'Service 2')

    def test_browser(self):
        service, api = _get_service()

        browser = service.browser

        api.set_cp_service.assert_called_once_with(12)
        self.assertIsInstance(browser, AppBrowser)

    def test_login(self):
        service, api = _get_service()

        service.login('test_username', 'test_password')

        api.set_cp_service.assert_called_once_with(12)
        api.set_sign_in.assert_called_once_with('test_username', 'test_password')

    def test_logout(self):
        service, api = _get_service()

        service.logout()

        api.set_cp_service.assert_called_once_with(12)
        api.set_sign_out.assert_called_once()
