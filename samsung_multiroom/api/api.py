"""Low level api to communicate with samsung multiroom speaker."""
import logging
import urllib.parse
import uuid

import requests

from .api_response import ApiResponse
from .api_stream import ApiStream

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

    def __init__(self, ip_address, port=55001, timeout=5):
        """
        Initialise endpoint.

        :param ip_address: IP address of the speaker to connect to
        :param port: Port to use, defaults to 55001
        :param timeout: Timeout in seconds
        """
        self._ip_address = ip_address
        self._port = port
        self._endpoint = 'http://{0}:{1}'.format(ip_address, port)
        self._timeout = timeout
        self._uuid = str(uuid.uuid1())

    @property
    def ip_address(self):
        """
        :returns: IP address of the host
        """
        return self._ip_address

    @property
    def port(self):
        """
        :returns: Port to use
        """
        return self._port

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

        url = '{0}/{1}?cmd={2}'.format(self._endpoint, command, urllib.parse.quote(payload))
        headers = {
            'mobileUUID': self._uuid,
            'mobileName': 'Wireless Audio',
            'mobileVersion': '1.0',
        }

        try:
            _LOGGER.debug('Request %s. Raw payload %s', url, payload)
            response = requests.get(url, headers=headers, timeout=self._timeout)

            return self._parse_response_text(response.text)
        except requests.exceptions.RequestException:
            _LOGGER.error('Request %s failed', url, exc_info=1)
            raise SamsungMultiroomApiException('Request {0} failed'.format(url))

    def _parse_response_text(self, response_text):
        _LOGGER.debug('Response %s', response_text)

        response = ApiResponse(response_text)

        if not response.success:
            raise SamsungMultiroomApiException('Received invalid response {0}'.format(response.raw))

        return response.data

    def get(self, command, action, params=None):
        """
        Generic GET request.

        :param command: COMMAND_* constant
        :param action: Get action name to execute e.g. GetVolume
        :param params: List of tuples (name, value, (optional) type hint str/dec/cdata)
        :returns dict
        """
        return self.request(METHOD_GET, command, format_payload(action, params))

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
        Get main information about speaker.

        :returns: Dict:
            - party - off
            - partymain - None
            - grouptype - one of M, S, N (Master, Slave, None?)
            - groupmainip - if speaker is in group, this is IP address of the master speaker
            - groupmainmacaddr - if speaker is in group, this is MAC address of the master speaker
            - spkmacaddr - this speaker's MAC address
            - spkmodelname - this speaker's model
            - groupmode - aasync, none
            - channeltype - front, invalid
            - channelvolume - 0
            - multichinfo - on
            - groupspknum - total number of speakers in the group
            - dfsstatus - dfsoff
            - protocolver - 2.3
            - btmacaddr - bluetooth MAC address
        """
        path = '/{0}?cmd={1}'.format(COMMAND_UIC, urllib.parse.quote(format_payload('GetMainInfo')))

        stream = ApiStream(self._ip_address, self._port, self._timeout)

        # Speaker sends two http responses for this request, latter one contains correct payload. We attempt
        # to fetch both responses and read/parse both.
        for response in stream.open(path):
            if not response.success:
                stream.close()
                _LOGGER.error('Request http://%s:%s%s failed', self._ip_address, self._port, path, exc_info=1)
                raise SamsungMultiroomApiException('Request http://{0}:{1}{2} failed'.format(
                    self._ip_address, self._port, path))

            if response.name == 'MainInfo':
                stream.close()
                return response.data

        _LOGGER.error('Request http://%s:%s%s failed', self._ip_address, self._port, path, exc_info=1)
        raise SamsungMultiroomApiException('Request http://{0}:{1}{2} failed'.format(
            self._ip_address, self._port, path))

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

        :param playback_control: resume|pause|play
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

    def set_search_time(self, play_time):
        """
        Set current track to play from a specific time.

        API call will fail unless track is currently played.

        Setting play time further than length of the track ends the current track and plays next from the beginning.

        :play_time: play time in seconds
        """
        self.get(COMMAND_UIC, 'SetSearchTime', [('playtime', int(play_time))])

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

        if not int(response['listcount']):
            return []

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

        if not int(response['listcount']):
            return []

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

        if not int(response['listcount']):
            return []

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

        if not int(response['listcount']):
            return []

        return response_list(response['musiclist']['music'])

    def set_playlist_playback_control(self, items):
        """
        Create a playlist and playback.

        Use pc_get_music_list_by_id() to fetch item information required for playlist item.

        :param items: List of dicts:
            - device_udn
            - object_id
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
            if 'artist' not in item:
                item['artist'] = 'Unknown'
            if 'thumbnail' not in item:
                item['thumbnail'] = ''

            params.append(('device_udn', item['device_udn']))
            params.append(('objectid', item['object_id']))
            params.append(('songtitle', item['title'], 'cdata'))
            params.append(('thumbnail', item['thumbnail'], 'cdata'))
            params.append(('artist', item['artist'], 'cdata'))

        self.get(COMMAND_UIC, 'SetPlaylistPlaybackControl', params)

    def browse_main(self, start_index, list_count):
        """
        Browse radios from the root.

        :param start_index:
        :param list_count:
        :returns: radio list item dict:
            folder:
            - @type - 0 - folder, 2 - radio
            - title - name of the folder
            - contentid - pass to get_select_radio_list() to browse into this folder
            radio:
            - @type - 0 - folder, 2 - radio
            - title - name of the radio
            - description - radio description
            - mediaid
            - thumbnail - URL
            - contentid
        """
        params = [
            ('startindex', int(start_index)),
            ('listcount', int(list_count)),
        ]

        response = self.get(COMMAND_CPM, 'BrowseMain', params)

        if not int(response['listcount']):
            return []

        return response_list(response['menulist']['menuitem'])

    def get_select_radio_list(self, content_id, start_index, list_count):
        """
        Browse specific radio folder.

        Note: you can't browse arbitrary folder. In order to browse a folder you had to navigate to it in a previous
        browse_main() or get_select_radio_list() call. This limitation is imposed by the speaker.

        :param content_id: contentid as returned from browse_main() or get_select_radio_list()
        :param start_index:
        :param list_count:
        :returns: see browse_main()
        """
        params = [
            ('contentid', int(content_id)),
            ('startindex', int(start_index)),
            ('listcount', int(list_count)),
        ]

        response = self.get(COMMAND_CPM, 'GetSelectRadioList', params)

        if not int(response['listcount']):
            return []

        return response_list(response['menulist']['menuitem'])

    def get_current_radio_list(self, start_index, list_count):
        """
        Browse previously browsed radio folder.

        :param start_index:
        :param list_count:
        :returns: see browse_main()
        """
        params = [
            ('startindex', int(start_index)),
            ('listcount', int(list_count)),
        ]

        response = self.get(COMMAND_CPM, 'GetCurrentRadioList', params)

        if not int(response['listcount']):
            return []

        return response_list(response['menulist']['menuitem'])

    def get_upper_radio_list(self, start_index, list_count):
        """
        Browse parent of a browsed radio folder.

        :param start_index:
        :param list_count:
        :returns: see browse_main()
        """
        params = [
            ('startindex', int(start_index)),
            ('listcount', int(list_count)),
        ]

        response = self.get(COMMAND_CPM, 'GetUpperRadioList', params)

        if not int(response['listcount']):
            return []

        return response_list(response['menulist']['menuitem'])

    def set_play_select(self, content_ids):
        """
        Plays selected radio or app item.

        :param content_ids: Content id as returned by get_upper_radio_list(), get_select_radio_list() or
            get_current_radio_list(), or list of content ids
        """
        if not isinstance(content_ids, list):
            content_ids = [content_ids]

        if len(content_ids) > 1:
            params = [('selectitemids', [int(id) for id in content_ids])]
        elif content_ids:
            params = [('selectitemid', int(content_ids[0]))]
        else:
            params = [('selectitemid', '')]

        self.get(COMMAND_CPM, 'SetPlaySelect', params)

    def get_station_data(self, content_id):
        """
        Get radio station data.

        :param content_id: Content id as returned by get_upper_radio_list(), get_select_radio_list() or
            get_current_radio_list()
        :returns: Station data dict:
            - cpname - likely TuneIn
            - title
            - description
            - thumbnail
            - stationurl
            - browsemode
            - timestamp
        """
        params = [('selectitemid', int(content_id))]

        return self.get(COMMAND_CPM, 'GetStationData', params)

    def get_7band_eq_list(self):
        """
        Retrieve equalizer presets.

        :returns: List of preset dicts with following attributes:
            - @index
            - presetindex
            - presetname
        """
        response = self.get(COMMAND_UIC, 'Get7BandEQList')

        return response_list(response['presetlist']['preset'])

    def get_current_eq_mode(self):
        """
        Retrieve current equalizer settings.

        :returns: Preset dict with following attributes:
            - presetindex
            - presetname
            - eqvalue1
            - eqvalue2
            - eqvalue3
            - eqvalue4
            - eqvalue5
            - eqvalue6
            - eqvalue7
        """
        response = self.get(COMMAND_UIC, 'GetCurrentEQMode')

        return response

    def set_7band_eq_value(self, preset_index, values):
        """
        Set preset's equalizer settings.

        Note, this doesn't overwrite preset settings, this method only sets those values temporarily. To overwrite use
        reset_7band_eq_value() method.

        :param preset_index:
        :param values: List of 7 integers ranging between -6 and 6
        """
        params = [('presetindex', int(preset_index))]

        for i, value in enumerate(values):
            params.append(('eqvalue' + str(i + 1), int(value)))

        self.get(COMMAND_UIC, 'Set7bandEQValue', params)

    def set_7band_eq_mode(self, preset_index):
        """
        Switch equalizer to a predefined preset.

        :param preset_index:
        """
        params = [('presetindex', int(preset_index))]

        self.get(COMMAND_UIC, 'Set7bandEQMode', params)

    def reset_7band_eq_value(self, preset_index, values):
        """
        Overwrite preset's equalizer settings.

        :param preset_index:
        :param values: List of 7 integers ranging between -6 and 6
        """
        params = [('presetindex', int(preset_index))]

        for i, value in enumerate(values):
            params.append(('eqvalue' + str(i + 1), int(value)))

        self.get(COMMAND_UIC, 'Reset7bandEQValue', params)

    def del_custom_eq_mode(self, preset_index):
        """
        Delete custom preset.

        Note, you cannot delete predefined presets with indices between 0 and 3 inculsive.

        :param preset_index:
        """
        params = [('presetindex', int(preset_index))]

        self.get(COMMAND_UIC, 'DelCustomEQMode', params)

    def add_custom_eq_mode(self, preset_index, preset_name):
        """
        Creates a new custom preset, using currently set equilizer values.

        Use set_7band_eq_value() or set_7band_eq_mode() to set equilizer values.

        It also allows to overwrite existing custom preset with current equilizer values.

        :param presetindex:
        :param presetname:
        """
        params = [('presetindex', int(preset_index)), ('presetname', preset_name)]

        self.get(COMMAND_UIC, 'AddCustomEQMode', params)

    def set_speaker_time(self, datetime):
        """
        Set speaker's internal time

        :param datetime: Datetime object e.g. datetime.datetime.now()
        """
        params = [
            ('year', datetime.year),
            ('month', datetime.month),
            ('day', datetime.day),
            ('hour', datetime.hour),
            ('min', datetime.minute),
            ('sec', datetime.second),
        ]

        self.get(COMMAND_UIC, 'SetSpeakerTime', params)

    def get_sleep_timer(self):
        """
        Get sleep timer settings
        :returns: Timer settings dict with following attributes:
            - sleepoption - off|start
            - sleeptime - remaining time in seconds
        """
        return self.get(COMMAND_UIC, 'GetSleepTimer')

    def set_sleep_timer(self, option, time):
        """
        Put speaker into sleep mode after specific time
        :param option: off|start
        :param time: delay in seconds
        """
        params = [
            ('option', option),
            ('sleeptime', int(time)),
        ]

        self.get(COMMAND_UIC, 'SetSleepTimer', params)

    def get_alarm_info(self):
        """
        Get list of set alarms.

        :returns: List of dicts:
            - @index - alarm id
            - hour - hour part of alarm
            - min - minutes part of alarm
            - week - hex of days flags Sun Mon Tue Wed Thu Fri Sat, e.g. for weekdays 00111110 - 0x3E
            - volume - volume of alarm
            - title - radio station title
            - description - radio station description
            - thumbnail - radio station thumbnail
            - stationurl - radio station URL
            - set - on|off whether alarm is active or not
            - soundenable - on|off whether predefined sound is used or not
            - sound - on|off whether predefined sound is used or not
            - alarmsoundname - name of predefined alarm sound names as returned by get_alarm_sound_list()
            - duration - duration of alarm in seconds
        """
        response = self.get(COMMAND_UIC, 'GetAlarmInfo')

        return response_list(response['alarmList']['alarm'])

    def set_alarm_on_off(self, index, alarm):
        """
        Enable/disable alarm.

        :param index: Alarm index
        :param alarm: on|off
        """
        params = [
            ('index', int(index)),
            ('alarm', alarm),
        ]

        self.get(COMMAND_UIC, 'SetAlarmOnOff', params)

    def get_alarm_sound_list(self):
        """
        Get list of predefined alarm sounds to use for alarm.

        :returns: List of dicts:
            - @index - alarm sound index
            - alarsoundindex - (note misspelling) alarm sound index
            - alarmsoundname - alarm sound name
        """
        response = self.get(COMMAND_UIC, 'GetAlarmSoundList')

        return response_list(response['alarmlist']['alarmsound'])

    def set_alarm_info(self, index, hour, minute, week, duration, volume, station_data):
        """
        Create alarm.

        Note, you can only create 3 alarms with indices 0, 1, and 2.

        :param index: Alarm index
        :param hour: Alarm hour
        :param minute: Alarm minute
        :param week: hex of days flags Sun Mon Tue Wed Thu Fri Sat, e.g. for weekdays 00111110 - 0x3E
        :param duration: Alarm duration in seconds
        :param volume: Alarm volume 0-100
        :param station_data: Dict as returned by get_station_data
            - title
            - description
            - thumbnail
            - stationurl
        """
        params = [
            ('index', int(index)),
            ('hour', int(hour)),
            ('min', int(minute)),
            ('week', hex(int(week, 16))),
            ('volume', int(volume)),
            ('title', station_data['title'], 'cdata'),
            ('description', station_data['description'], 'cdata'),
            ('thumbnail', station_data['thumbnail'], 'cdata'),
            ('stationurl', station_data['stationurl'], 'cdata'),
            ('soundenable', 'off'),
            ('sound', -1),
            ('duration', int(duration)),
        ]

        self.get(COMMAND_UIC, 'SetAlarmInfo', params)

    def del_alarm(self, index_list):
        """
        Delete alarm(s).

        Note, speaker's have a limit of 3 alarms and only the first 3 indices will be accepted for deletion while
        remaining will be ignored. This restriction is set on the speaker itself.

        :param index_list: List of alarm indices as returned by get_alarm_info()
        """
        params = [
            ('totaldelnum', len(index_list)),
        ]
        params += [('index', int(i)) for i in index_list]

        self.get(COMMAND_UIC, 'DelAlarm', params)

    def spk_in_group(self, action):
        """
        ???

        :param action: select|?
        """
        params = [('act', action)]

        return self.get(COMMAND_UIC, 'SpkInGroup', params)

    def set_multispk_group(self, name, speakers):
        """
        Group speakers.

        :param name: Group's name
        :param speakers: List of speakers (first one will be treated as main/control one). Dict:
            - name
            - ip
            - mac
        """
        params = [('name', name, 'cdata'), ('index', 1), ('type', 'main'), ('spknum', len(speakers))]

        for i, speaker in enumerate(speakers):
            if i == 0:
                params += [
                    ('audiosourcemacaddr', speaker['mac']),
                    ('audiosourcename', speaker['name'], 'cdata'),
                    ('audiosourcetype', 'speaker'),
                ]
            else:
                params += [
                    ('subspkip', speaker['ip']),
                    ('subspkmacaddr', speaker['mac']),
                ]

        self.get(COMMAND_UIC, 'SetMultispkGroup', params)

    def set_ungroup(self):
        """
        Ungroup speakers.
        """
        self.get(COMMAND_UIC, 'SetUngroup')

    def get_cp_list(self, start_index, list_count):
        """
        Get list of speakers app integrations.

        :returns: List of dicts:
            - cpid - id of app service
            - cpname - service name
            - signinstatus - 0/1
            - username - (optionally if signed in) signed in user name
            - istrial_user - (optionally) 1
        """
        params = [
            ('liststartindex', int(start_index)),
            ('listcount', int(list_count)),
        ]

        response = self.get(COMMAND_CPM, 'GetCpList', params)

        return response_list(response['cplist']['cp'])

    def set_cp_service(self, cp_id):
        """
        Switch to a specific cp service.

        It also initiates playback of that service.

        :param cp_id: Cp service id as returned by get_cp_list()
        """
        params = [('cpservice_id', int(cp_id))]

        self.get(COMMAND_CPM, 'SetCpService', params)

    def get_cp_info(self):
        """
        Get info about currently active cp service.

        :returns: Dict
            - cpname
            - timestamp - ISO format
            - category
            - signinstatus - 0/1
            - username
            - subscription_info
            - audioinfo - Dict
                - title
                - streamtype - station|?
                - thumbnail - thumbnail url
                - playstatus - play|pause
            },
        """
        return self.get(COMMAND_CPM, 'GetCpInfo')

    def set_sign_in(self, username, password):
        """
        Authenticate with the currently active service.

        :param username: Service username
        :param password: Service password
        """
        params = [
            ('username', username),
            ('password', password),
        ]

        self.get(COMMAND_CPM, 'SetSignIn', params)

    def set_sign_out(self):
        """
        Sign out from the currently active service.

        You need to be authenticated for this call to be successful.
        """
        self.get(COMMAND_CPM, 'SetSignOut')

    def get_cp_submenu(self):
        """
        Get list of top level service categories.

        :returns: List of dicts:
            - @id - id of the menu item
            - submenuitem_localized - menu item name
        """
        response = self.get(COMMAND_CPM, 'GetCpSubmenu')

        return response_list(response['submenu']['submenuitem'])

    def set_select_cp_submenu(self, content_id, start_index, list_count):
        """
        Get list of sub categories.

        Note, some items are autoplayable. By calling this method you might initiate playback.

        :param content_id: parent id as returned by get_cp_submenu() or this method
        :returns: List of dicts
            - @type
            - title
            - contentid
        """
        params = [
            ('contentid', int(content_id)),
            ('startindex', int(start_index)),
            ('listcount', int(list_count)),
        ]

        response = self.get(COMMAND_CPM, 'SetSelectCpSubmenu', params)

        return response_list(response['menulist']['menuitem'])

    def get_cp_player_playlist(self, start_index, list_count):
        """
        Get currently active service playlist.

        Note, some services have limit of items returned regardless of list_count passed.

        :param start_index:
        :param list_count:
        :returns: List of dicts
            - @type - 1
            - @available - 0/1
            - @currentplaying - (optional) 1 if present
            - artist
            - album
            - mediaid - unique
            - tracklength - track length in seconds
            - title
            - contentid
            - thumbnail - thumbnail url

        """
        params = [
            ('startindex', int(start_index)),
            ('listcount', int(list_count)),
        ]

        response = self.get(COMMAND_CPM, 'GetCpPlayerPlaylist', params)

        return response_list(response['menulist']['menuitem'])

    def set_skip_current_track(self):
        """
        Skip current track and play next item on the playlist.
        """
        self.get(COMMAND_CPM, 'SetSkipCurrentTrack')

    def get_current_play_time(self):
        """
        Get info about current track playback position and length.

        :returns: Dict
            - tracklength - track length in seconds
            - playtime - playback position in seconds
        """
        return self.get(COMMAND_UIC, 'GetCurrentPlayTime')

    def set_play_cp_playlist_track(self, item_id):
        """
        Advance playback to specific track on the playlist.

        :param item_id: Item id as returned by get_cp_player_playlist()
        """
        params = [('selectitemid', int(item_id))]

        return self.get(COMMAND_CPM, 'SetPlayCpPlaylistTrack', params)


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
    """
    Format request parameter.

    :param param: Tuple e.g. ('list_count', 30, 'dec')
        - name - name of the param
        - value - mixed value
        - type_hint - (optionally) str|dec|cdata|dec_arr
    """
    (name, value, *attributes) = param

    if not attributes:
        type_hint = 'str'
        if isinstance(value, int):
            type_hint = 'dec'
        if isinstance(value, list) and value and isinstance(value[0], int):
            type_hint = 'dec_arr'
    else:
        type_hint = attributes[0]

    if type_hint == 'cdata':
        return '<p type="{0}" name="{1}" val="empty"><![CDATA[{2}]]></p>'.format(type_hint, name, value)
    if type_hint == 'dec_arr':
        value = ''.join(['<item>{0}</item>'.format(v) for v in value])
        return '<p type="{0}" name="{1}" val="empty">{2}</p>'.format(type_hint, name, value)

    return '<p type="{0}" name="{1}" val="{2}"/>'.format(type_hint, name, value)


def format_payload(action, params=None):
    """Format full request payload."""
    payload = format_action(action)
    if params:
        for param in params:
            payload += format_param(param)

    return payload


def paginator(*args):
    """
    Generator to paginate over api call.

    Api method must accept start_index and list_count parameters.

    :param: callable function to use for pagination
    :param: optionally pass second function that will be used for subsequent pages
    :param: pass all initial values that first callable function accepts, they will be replicated to a second callable
    :returns: Iterable
    """
    if not callable(args[0]):
        raise ValueError('First argument must be a function')

    primary = args[0]
    secondary = args[0]
    args = args[1:]

    if callable(args[0]):
        secondary = args[0]
        args = args[1:]

    import inspect
    primary_parameters = inspect.signature(primary).parameters.keys()
    secondary_parameters = inspect.signature(secondary).parameters.keys()

    # match primary_parameters with args
    primary_kwargs = {}
    secondary_kwargs = {}

    for i, parameter in enumerate(primary_parameters):
        primary_kwargs[parameter] = args[i]
        if parameter in secondary_parameters:
            secondary_kwargs[parameter] = args[i]

    current = primary
    current_kwargs = primary_kwargs
    has_more = True

    while has_more:
        items = current(**current_kwargs)
        for item in items:
            yield item

        has_more = len(items) >= current_kwargs['list_count']

        current = secondary
        current_kwargs = secondary_kwargs
        current_kwargs['start_index'] = current_kwargs['start_index'] + current_kwargs['list_count']
