"""DLNA service."""
from ..service import Service
from .browser import DlnaBrowser


class DlnaService(Service):
    """
    Dlna service.
    """

    def __init__(self, api):
        super().__init__(DlnaBrowser(api))

    @property
    def name(self):
        """
        :returns: Name of the service
        """
        return 'dlna'
