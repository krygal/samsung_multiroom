import unittest
from unittest.mock import MagicMock

from samsung_multiroom.service import ServiceRegistry
from samsung_multiroom.service.app import AppService
from samsung_multiroom.service.dlna import DlnaService
from samsung_multiroom.service.tunein import TuneInService


def _get_service_registry():
    api = MagicMock()
    api.get_cp_list.return_value = [
        {
            'cpid': '0',
            'cpname': 'Signed out service',
            'signinstatus': '0',
        },
        {
            'cpid': '1',
            'cpname': 'Signed in service',
            'signinstatus': '1',
            'username': 'service_username',
        },
        {
            'cpid': '2',
            'cpname': 'Service 2',
            'signinstatus': '0',
        },
        {
            'cpid': '3',
            'cpname': 'Service 3',
            'signinstatus': '0',
        }
    ]

    service_registry = ServiceRegistry(api)

    return (service_registry, api)


class TestServiceRegistry(unittest.TestCase):

    @unittest.mock.patch('samsung_multiroom.api.api._get_callable_parameters')
    def test_get_services_names(self, signature):
        signature.side_effect = [['start_index', 'list_count']] * 2

        service_registry, api = _get_service_registry()

        services_names = service_registry.get_services_names()

        self.assertEqual(services_names, ['dlna', 'tunein', 'Signed out service', 'Signed in service', 'Service 2', 'Service 3'])

    @unittest.mock.patch('samsung_multiroom.api.api._get_callable_parameters')
    def test_service_dlna(self, signature):
        signature.side_effect = [['start_index', 'list_count']] * 2

        service_registry, api = _get_service_registry()

        service = service_registry.service('dlna')

        self.assertIsInstance(service, DlnaService)
        self.assertEqual(service.name, 'dlna')

    @unittest.mock.patch('samsung_multiroom.api.api._get_callable_parameters')
    def test_service_tunein(self, signature):
        signature.side_effect = [['start_index', 'list_count']] * 2

        service_registry, api = _get_service_registry()

        service = service_registry.service('tunein')

        self.assertIsInstance(service, TuneInService)
        self.assertEqual(service.name, 'tunein')

    @unittest.mock.patch('samsung_multiroom.api.api._get_callable_parameters')
    def test_service_app(self, signature):
        signature.side_effect = [
            ['start_index', 'list_count'],
            ['start_index', 'list_count'],
        ]

        service_registry, api = _get_service_registry()

        service = service_registry.service('Service 2')

        self.assertIsInstance(service, AppService)
        self.assertEqual(service.name, 'Service 2')
