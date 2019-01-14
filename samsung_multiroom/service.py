"""
Speaker music service integrations.
"""
import abc

from .api import paginator
from .browser import AppBrowser
from .browser import DlnaBrowser
from .browser import TuneInBrowser


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


class Service(metaclass=abc.ABCMeta):
    """
    Abstract service
    """

    @property
    @abc.abstractmethod
    def name(self):
        """
        :returns: Name of the service
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def browser(self):
        """
        :returns: Compatible Browser instance for this service
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def login(self, username, password):
        """
        Authenticate with username/password.

        :param username:
        :param password:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def logout(self):
        """
        Reset authentication state.
        """
        raise NotImplementedError()


class DlnaService(Service):
    """
    Dlna service.
    """

    def __init__(self, api):
        self._browser = DlnaBrowser(api)

    @property
    def name(self):
        """
        :returns: Name of the service
        """
        return 'dlna'

    @property
    def browser(self):
        """
        :returns: Compatible Browser instance for this service
        """
        return self._browser

    def login(self, username, password):
        """
        Dlna service does not require prior authentication.
        """

    def logout(self):
        """
        Dlna service does not require prior authentication.
        """


class TuneInService(Service):
    """
    TuneIn radio service.
    """

    def __init__(self, api):
        self._browser = TuneInBrowser(api)

    @property
    def name(self):
        """
        :returns: Name of the service
        """
        return 'tunein'

    @property
    def browser(self):
        """
        :returns: Compatible Browser instance for this service
        """
        return self._browser

    def login(self, username, password):
        """
        TuneIn service does not require prior authentication.
        """

    def logout(self):
        """
        TuneIn service does not require prior authentication.
        """


class AppService(Service):
    """
    Generic music streaming app service.
    """

    def __init__(self, api, app_id, app_name):
        self._api = api
        self._id = app_id
        self._name = app_name

        self._browser = AppBrowser(api, app_id, app_name)

    @property
    def name(self):
        """
        :returns: Name of the service
        """
        return self._name

    @property
    def browser(self):
        """
        :returns: Compatible Browser instance for this service
        """
        self._api.set_cp_service(self._id)
        return self._browser

    def login(self, username, password):
        """
        Authenticate with username/password.

        :param username:
        :param password:
        """
        self._api.set_cp_service(self._id)
        self._api.set_sign_in(username, password)

    def logout(self):
        """
        Reset authentication state.
        """
        self._api.set_cp_service(self._id)
        self._api.set_sign_out()
