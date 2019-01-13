"""
Parse API XML response.
"""
import xmltodict


class ApiResponse:
    """
    Extract key information from api response body text.
    """

    def __init__(self, response_text):
        self._name = None
        self._success = None
        self._data = None
        self._raw = None

        self._parse(response_text)

    @property
    def name(self):
        """
        :returns: resopnse type/name
        """
        return self._name

    @property
    def success(self):
        """
        :returns: True if response was successful
        """
        return self._success

    @property
    def data(self):
        """
        :returns: response data
        """
        return self._data

    @property
    def raw(self):
        """
        :returns: Raw response text
        """
        return self._raw

    def _parse(self, response_text):
        self._success = False
        self._raw = response_text

        try:
            response_dict = xmltodict.parse(response_text)
        except xmltodict.expat.ExpatError:
            return

        # for some requests speaker returns command in response that does not match request command
        try:
            response_command = next(iter(response_dict))

            self._name = response_dict[response_command]['method']
            self._data = response_dict[response_command]['response']
            self._success = (self._data['@result'] == 'ok')

            # redundant
            del self._data['@result']

            return
        except KeyError:
            pass
