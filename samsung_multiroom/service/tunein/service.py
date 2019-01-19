"""TuneIn service."""
from ..service import Service
from .browser import TuneInBrowser


class TuneInService(Service):
    """
    TuneIn radio service.
    """

    def __init__(self, api):
        super().__init__(TuneInBrowser(api))

    @property
    def name(self):
        """
        :returns: Name of the service
        """
        return 'tunein'
