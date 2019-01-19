"""Generic music streaming app service."""
from ..service import Service
from .browser import AppBrowser


class AppService(Service):
    """
    Generic music streaming app service.
    """

    def __init__(self, api, app_id, app_name):
        super().__init__(AppBrowser(api, app_id, app_name))

        self._api = api
        self._id = app_id
        self._name = app_name

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
        return super().browser

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
