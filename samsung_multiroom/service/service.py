"""Speaker music service integrations."""
import abc


class Service(metaclass=abc.ABCMeta):
    """
    Abstract service
    """

    def __init__(self, browser):
        """
        :param browser: Browser instance specific to implementing service
        """
        self._browser = browser

    @property
    @abc.abstractmethod
    def name(self):
        """
        :returns: Name of the service
        """
        raise NotImplementedError()

    @property
    def browser(self):
        """
        :returns: Compatible Browser instance for this service
        """
        return self._browser

    def login(self, username, password):
        """
        Authenticate with username/password.

        :param username:
        :param password:
        """

    def logout(self):
        """
        Reset authentication state.
        """
