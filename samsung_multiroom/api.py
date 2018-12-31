"""Low level api to communicate with samsung multiroom speaker."""
import logging
import urllib.parse

import requests
import xmltodict

METHOD_GET = 'get'

COMMAND_UIC = 'UIC'
COMMAND_CPM = 'CPM'

_LOGGER = logging.getLogger(__name__)


class SamsungMultiroomApiException(Exception):
    """Generic API exception."""


class SamsungMultiroomApi:
    """
    Samsung Multiroom Api implementation.

    Contains non-inclusive list of API calls you can make to control the speaker.
    """

    def __init__(self, ip_address, port=55001):
        """
        Initialise endpoint.

        :param ip_address: IP address of the speaker to connect to
        :param port: Port to use, defaults to 55001
        """
        self.endpoint = 'http://{0}:{1}'.format(ip_address, port)

    def request(self, method, command, payload):
        """
        Makes a request to a configured endpoint.

        :param method: HTTP method to use
        :param command: UIC|CPM
        :param payload: XML string with payload
        :returns: Response dict
        :raises: ValueError
        :raises: SamsungMultiroomApiException
        """
        if method not in [METHOD_GET]:
            raise ValueError('Invalid method {0}, must be one of METHOD_* constants'.format(method))

        if command not in [COMMAND_UIC, COMMAND_CPM]:
            raise ValueError('Invalid command {0}, must be one of COMMAND_* constants'.format(method))

        url = '{0}/{1}?cmd={2}'.format(self.endpoint, command, urllib.parse.quote(payload))

        try:
            _LOGGER.debug('Request %s. Raw payload %s', url, payload)
            response = requests.get(url)
            _LOGGER.debug('Response %s', response.text)

            try:
                dict_response = xmltodict.parse(response.text)
            except Exception:
                _LOGGER.error('Failed to parse a resopnse %s', response.text, exc_info=1)
                raise SamsungMultiroomApiException('Received invalid response {0}'.format(response.text))

            # for some requests speaker returns command in response that does not match request command
            for response_command in [COMMAND_UIC, COMMAND_CPM]:
                try:
                    dict_response_response = dict_response[response_command]['response']
                    if dict_response_response['@result'] != 'ok':
                        raise SamsungMultiroomApiException('Received invalid response {0}'.format(response.text))

                    del dict_response_response['@result']
                    return dict_response_response
                except KeyError:
                    pass

            raise SamsungMultiroomApiException('Received invalid response {0}'.format(response.text))
        except requests.exceptions.RequestException:
            _LOGGER.error('Request %s failed', url, exc_info=1)
            raise SamsungMultiroomApiException('Request {0} failed'.format(url))

    def get(self, command, action, params=None):
        """
        Generic GET request.

        :param command: COMMAND_* constant
        :param action: Get action name to execute e.g. GetVolume
        :param params: List of tuples (name, value, (optional) type hint str/dec/cdata)
        :returns dict
        """
        payload = format_action(action)
        if params:
            for param in params:
                payload += format_param(param)

        return self.request(METHOD_GET, command, payload)

    def get_speaker_name(self):
        """
        :returns: Speaker name
        """
        return self.get(COMMAND_UIC, 'GetSpkName')['spkname']

    def set_speaker_name(self, name):
        """
        Set speaker name.

        :param name: new speaker name
        """
        self.get(COMMAND_UIC, 'SetSpkName', [('spkname', name, 'cdata')])

    def get_main_info(self):
        """
        :returns: Empty dict
        """
        self.get(COMMAND_UIC, 'GetMainInfo')

    def get_volume(self):
        """
        Get current volume level between 0 and 100.

        :returns: int - volume level
        """
        return int(self.get(COMMAND_UIC, 'GetVolume')['volume'])

    def set_volume(self, volume):
        """
        Set speaker volume level.

        :param volume: Volume level between 0 and 100
        """
        self.get(COMMAND_UIC, 'SetVolume', [('volume', int(volume))])

    def get_mute(self):
        """
        Get mute state of the speaker.

        :returns: boolean True if muted
        """
        return on_off_bool(self.get(COMMAND_UIC, 'GetMute')['mute'])

    def set_mute(self, mute):
        """
        Mute/unmute the speaker.

        :param mute: boolean True to mute
        """
        self.get(COMMAND_UIC, 'SetMute', [('mute', bool_on_off(mute))])

    def get_func(self):
        """
        Retrieve current source for the speaker.

        :returns: Dict with
            - function - aux|bt|hdmi|optical|soundshare|wifi
            - submode - dlna|cp|?
        """
        return self.get(COMMAND_UIC, 'GetFunc')

    def set_func(self, function):
        """
        Set the source for the speaker

        :param function: aux|bt|hdmi|optical|soundshare|wifi
        """
        self.get(COMMAND_UIC, 'SetFunc', [('function', function)])

    def get_shuffle_mode(self):
        """
        Retrieve currently set shuffle mode.

        :returns: Boolean True if shuffle mode is enabled
        """
        return on_off_bool(self.get(COMMAND_UIC, 'GetShuffleMode')['shuffle'])

    def set_shuffle_mode(self, shuffle_mode):
        """
        Enable/disable shuffle mode of the playlist.

        :param shuffle_mode: boolean
        """
        self.get(COMMAND_UIC, 'SetShuffleMode', [('shufflemode', bool_on_off(shuffle_mode))])

    def set_trick_mode(self, trick_mode):
        """
        Move to next/previous track on the playlist.

        :param trick_mode: previous|next
        """
        if trick_mode not in ['previous', 'next']:
            raise ValueError('Trick mode must one of: previous, next')

        self.get(COMMAND_UIC, 'SetTrickMode', [('trickmode', trick_mode)])

    def set_playback_control(self, playback_control):
        """
        Pause/resume current playlist.

        :param playback_control: resume|pause
        """
        if playback_control not in ['resume', 'pause']:
            raise ValueError('Playback control must be one of: resume, pause')

        self.get(COMMAND_UIC, 'SetPlaybackControl', [('playbackcontrol', playback_control)])

    def get_music_info(self):
        """
        Get detailed information about current track on the playlist.

        :returns: Dict with
            - device_udn - source device unique identifier
            - playertype - allshare
            - playbacktype - folder|playlist
            - sourcename
            - parentid
            - parentid2
            - objectid
            - title
            - artist
            - album
            - thumbnail
            - timelength - HH:MM:SS.uuu format
            - playtime - in microseconds
            - seek - enable|?
            - pause - enable|?
        """
        return self.get(COMMAND_UIC, 'GetMusicInfo')

    def get_play_status(self):
        """
        Get information about play/pause status for the playlist.

        :returns: Dict with
            - function - wifi|?
            - submode - dlna|cp
            - playstatus - (optional) play|pause
        """
        return self.get(COMMAND_UIC, 'GetPlayStatus')

    def get_preset_list(self, start_index, list_count):
        """
        Get list of predefined radios.

        :param start_index: Starting position to retrieve
        :param list_count: Total number of items to retrieve
        :returns: List of dicts
            - title
            - description
            - thumbnail
            - contentid
            - mediaid
        """
        response = self.get(COMMAND_CPM, 'GetPresetList', [
            ('startindex', int(start_index)),
            ('listcount', int(list_count)),
        ])

        return response_list(response['presetlist']['preset'])

    def get_radio_info(self):
        """
        Retrieves currently selected radio info and play status.

        :returns: Dict
            - cpname - TuneIn|Unknown|?
            - playstatus - stop|play
            Optionally:
            - root - preset category
            - presetindex -  position on the preset list
            - title - name of the radio
            - description - description of the radio, can include the currently played song
            - thumbnail - URL of the radio thumbnail image
            - mediaid
            - allowfeedback
            - timestamp - in ISO 8601 format
            - noqueue
        """
        return self.get(COMMAND_CPM, 'GetRadioInfo')

    def set_play_preset(self, preset_type, preset_index):
        """
        Select radio of a particular index.

        Combine this with set_select_radio to play selected radio.

        :param preset_type: 1 - speaker, 0 - my
        :param preset_index: Index of get preset list
        """
        self.get(COMMAND_CPM, 'SetPlayPreset', [
            ('presettype', int(preset_type)),
            ('presetindex', int(preset_index)),
        ])

    def set_select_radio(self):
        """
        Play selected preset preset.

        Precede this with set_play_preset.
        """
        self.get(COMMAND_CPM, 'SetSelectRadio')

    def get_dms_list(self, start_index, list_count):
        """
        Retrieve list of DLNA compatible devices to use as a media source.

        :param start_index:
        :param list_count:
        :returns: List of DLNA devices dicts
            - @device_id - likely a sequential id
            - dmsid - device udn e.g. uuid:00113249-398f-0011-8f39-8f3949321100
            - dmsname - device name e.g. nas
            - devicetype - e.g. network
            - thumbnail_PNG_LRG - thumbnail url
            - thumbnail_JPG_LRG - thumbnail url
            - thumbnail_PNG_SM - thumbnail url
            - thumbnail_JPG_SM - thumbnail url
        """
        response = self.get(COMMAND_UIC, 'GetDmsList', [
            ('liststartindex', int(start_index)),
            ('listcount', int(list_count)),
        ])

        return response_list(response['dmslist']['dms'])

    def pc_get_music_list_by_category(self, device_udn, start_index, list_count):
        """
        Browse containers at the root of the DLNA device.

        :param device_udn: dmsid returned by get_dms_list()
        :param start_index:
        :param list_count:
        :returns: List of category dicts
            - @object_id - use it to browse into this container
            - type - usually CONTAINER
            - playindex - -1 for CONTAINERs
            - name - folder name
            - title - None
            - artist - None
            - album - None
            - thumbnail - None
            - timelength - None
            - device_udn -
        """
        response = self.get(COMMAND_UIC, 'PCGetMusicListByCategory', [
            ('device_udn', device_udn),
            ('filter', 'folder'),
            ('categoryid', 'folder'),
            ('liststartindex', int(start_index)),
            ('listcount', int(list_count)),
        ])

        return response_list(response['musiclist']['music'])

    def pc_get_music_list_by_id(self, device_udn, parent_id, start_index, list_count):
        """
        Browse containers/audio items in the container of the DLNA device.

        :param device_udn: dmsid returned by get_dms_list()
        :param parent_id: object_id as returned by pc_get_music_list_by_category or this method
        :param start_index:
        :param list_count:
        :returns: List of containers/audio items dicts
            - @object_id - e.g. 22$@52941
            - type - CONTAINER|AUDIO
            - playindex - -1 for CONTAINER, sequential for AUDIO
            - name - folder/file name
            - title
            - artist
            - album
            - thumbnail - URL
            - timelength - HH:MM:SS.xxx format
            - device_udn -
        """
        response = self.get(COMMAND_UIC, 'PCGetMusicListByID', [
            ('device_udn', device_udn),
            ('filter', 'folder'),
            ('parentid', str(parent_id)),
            ('liststartindex', int(start_index)),
            ('listcount', int(list_count)),
        ])

        return response_list(response['musiclist']['music'])

    def set_playlist_playback_control(self, items):
        """
        Create a playlist and playback.

        Use pc_get_music_list_by_id() to fetch item information required for playlist item.

        :param items: List of dicts:
            - device_udn
            - objectid
            - title - song title
            - artist - song artist
            - thumbnail - URL
        """
        params = [
            ('playbackcontrol', 'play'),
            ('playertype', 'allshare'),
            ('sourcename', '', 'cdata'),
            ('playindex', 0),
            ('playtime', 0),
            ('totalobjectcount', len(items)),
        ]

        for item in items:
            if 'title' not in item:
                item['title'] = 'Unknown'
            if 'title' not in item:
                item['artist'] = 'Unknown'
            if 'title' not in item:
                item['thumbnail'] = ''

            params.append(('device_udn', item['device_udn']))
            params.append(('objectid', item['objectid']))
            params.append(('songtitle', item['title'], 'cdata'))
            params.append(('thumbnail', item['thumbnail'], 'cdata'))
            params.append(('artist', item['artist'], 'cdata'))

        self.get(COMMAND_UIC, 'SetPlaylistPlaybackControl', params)


def on_off_bool(value):
    """Convert on/off to True/False correspondingly."""
    return value == 'on'


def bool_on_off(value):
    """Convert True/False to on/off correspondingly."""
    return 'on' if value else 'off'


def response_list(input_list):
    """xmltodict returns different structure if there's one item on the list."""
    if isinstance(input_list, dict):
        input_list = [input_list]

    return input_list


def format_action(action):
    """Format request action."""
    return '<name>{0}</name>'.format(action)


def format_param(param):
    """Format request parameter."""
    (name, value, *attributes) = param

    if not attributes:
        type_hint = 'str'
        if isinstance(value, int):
            type_hint = 'dec'
    else:
        type_hint = attributes[0]

    if type_hint == 'cdata':
        return '<p type="{0}" name="{1}" val="empty"><![CDATA[{2}]]></p>'.format(type_hint, name, value)

    return '<p type="{0}" name="{1}" val="{2}"/>'.format(type_hint, name, value)
