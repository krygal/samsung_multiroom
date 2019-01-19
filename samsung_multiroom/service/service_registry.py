"""Entry point for service initialisation."""
from ..api import paginator
from .app import AppService
from .dlna import DlnaService
from .tunein import TuneInService


class ServiceRegistry:
    """
    Entry point for service initialisation.
    """

    def __init__(self, api):
        """
        :param api:
        """
        self._api = api

    def get_services_names(self):
        """
        Get list of supported services names.

        :returns: List
        """
        base_names = [
            'dlna',
            'tunein',
        ]

        app_list = self._get_app_list()
        app_names = [s['cpname'] for s in app_list]

        return base_names + app_names

    def service(self, name):
        """
        Get service by name.

        :returns: Service instance
        """
        base_services = {
            'dlna': DlnaService(self._api),
            'tunein': TuneInService(self._api),
        }

        app_list = self._get_app_list()
        app_services = {s['cpname']: AppService(self._api, s['cpid'], s['cpname']) for s in app_list}

        return {**base_services, **app_services}[name]

    def _get_app_list(self):
        return paginator(self._api.get_cp_list, 0, 30)
