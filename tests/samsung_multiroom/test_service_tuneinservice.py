import unittest
from unittest.mock import MagicMock

from samsung_multiroom.browser import TuneInBrowser
from samsung_multiroom.service import TuneInService


def _get_service():
    api = MagicMock()

    service = TuneInService(api)

    return (service, api)


class TestTuneInService(unittest.TestCase):

    def test_name(self):
        service, api = _get_service()

        self.assertEqual(service.name, 'tunein')

    def test_browser(self):
        service, api = _get_service()

        browser = service.browser

        self.assertIsInstance(browser, TuneInBrowser)

    def test_login(self):
        service, api = _get_service()

        service.login('test_username', 'test_password')

        api.set_sign_in.assert_not_called()

    def test_logout(self):
        service, api = _get_service()

        service.logout()

        api.set_sign_out.assert_not_called()
