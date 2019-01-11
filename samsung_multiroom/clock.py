"""
Control speaker's clock functions.
"""
import abc
import datetime


class ClockBase(metaclass=abc.ABCMeta):
    """
    Clock interface to control time functions of the speaker.
    """

    def set_time(self, speaker_datetime=None):
        """
        Set speaker's current time.

        :param speaker_datetime: Datetime object
        """
        raise NotImplementedError()

    @property
    def alarm(self):
        """
        :returns: Alarm instance
        """
        raise NotImplementedError()

    @property
    def timer(self):
        """
        :returns: Timer instance
        """
        raise NotImplementedError()


class Clock(ClockBase):
    """
    Control time functions of the speaker.
    """

    def __init__(self, api, timer, alarm):
        """
        :param api: SamsungMultiroomApi instance
        """
        self._api = api
        self._timer = timer
        self._alarm = alarm

    def set_time(self, speaker_datetime=None):
        """
        Set speaker's current time.

        :param speaker_datetime: Datetime object
        """
        if speaker_datetime is None:
            speaker_datetime = datetime.datetime.now()

        self._api.set_speaker_time(speaker_datetime)

    @property
    def alarm(self):
        """
        :returns: Alarm instance
        """
        return self._alarm

    @property
    def timer(self):
        """
        :returns: Timer instance
        """
        return self._timer


class ClockGroup(ClockBase):
    """
    Control time functions for the group of the speakers.

    Due to the nature of alarms and timers, it is only required to use those on the main speaker of the group.
    """

    def __init__(self, clocks):
        """
        :param clocks: List of Clock instances
        """
        self._clocks = clocks

    @property
    def clocks(self):
        """
        :returns: List of Clock instances in group
        """
        return self._clocks

    def set_time(self, speaker_datetime=None):
        """
        Set current time for all speakers in group.

        :param speaker_datetime: Datetime object
        """
        for clock in self._clocks:
            clock.set_time(speaker_datetime)

    @property
    def alarm(self):
        """
        It is not possible to update alarm functions while the speaker is part of a group.

        :returns: Alarm instance of the first clock
        """
        return self._clocks[0].alarm

    @property
    def timer(self):
        """
        :returns: Timer instance of the first clock
        """
        return self._clocks[0].timer


class Timer:
    """
    Control timer to put speaker into sleep mode.
    """

    def __init__(self, api):
        """
        :param api: SamsungMultiroomApi instance
        """
        self._api = api

    def start(self, delay):
        """
        Set timer to put speaker into sleep mode after delay.

        :param delay: Delay in seconds
        """
        self._api.set_sleep_timer('start', delay)

    def stop(self):
        """
        Stop the timer.
        """
        self._api.set_sleep_timer('off', 0)

    def get_remaining_time(self):
        """
        :returns: Remaining timer seconds, or 0 if not enabled.
        """
        return int(self._api.get_sleep_timer()['sleeptime'])


class Alarm:
    """
    Control alarm functions of the speaker to wake speaker at specific time.
    """

    def __init__(self, api):
        """
        :param api: SamsungMultiroomApi instance
        """
        self._api = api
        self._slots = [None, None, None]

    def __getitem__(self, i):
        return self.get_slots()[i]

    def slot(self, i):
        """
        Get slot of a specific index.

        :param i: Slot index, must be between 0 and 2
        :returns: AlarmSlot instance
        """
        if i < 0 or i > 2:
            raise ValueError('Only three slots are available')

        return self.get_slots()[i]

    def get_slots(self):
        """
        Get alarm slots.

        Speakers have 3 alarm slots available. This method will return the ones that are set as well as empty ones to
        use for setting new alarms.

        :returns: List of AlarmSlot instances
        """
        alarms = self._api.get_alarm_info()

        for alarm in alarms:
            index = int(alarm['@index'])
            self._slots[index] = AlarmSlot(self._api, index, alarm)

        # fill with empty slots
        for index in range(3):
            if self._slots[index] is None:
                self._slots[index] = AlarmSlot(self._api, index)

        return self._slots


class AlarmSlot:
    """
    Specific alarm configuration.

    Speakers are limited to have only three alarms set at any given time. Alarm slot represents a single alarm,
    configured or not.
    """

    def __init__(self, api, index, alarm_info=None):
        """
        :param api: SamsungMultiroomApi instance
        :param index: Slot index
        """
        self._api = api
        self._index = index

        if alarm_info:
            self._time = '{0}:{1:02d}'.format(int(alarm_info['hour']), int(alarm_info['min']))
            self._weekdays = hexweek_to_weekday_list(alarm_info['week'])
            self._volume = int(alarm_info['volume'])
            self._duration = int(alarm_info['duration'])
            self._enabled = alarm_info['set'] == 'on'
            self._station_data = {
                'title': alarm_info['title'],
                'description': alarm_info['description'],
                'thumbnail_url': alarm_info['thumbnail'],
                'station_url': alarm_info['stationurl'],
            }
        else:
            self._set_defaults()

    def _set_defaults(self):
        self._time = datetime.datetime.now().strftime('%H:%M')
        self._weekdays = [datetime.datetime.now().weekday()]
        self._duration = 0
        self._volume = 5
        self._station_data = None
        self._enabled = False

    def set(self, time=None, weekdays=None, duration=None, volume=None, station_data=None, playlist=None, enabled=None):
        """
        Update speaker's configuration for this slot.

        :param time: hour/minute when to trigger the alarm in HH:MM format
        :param weekdays: List of integers representing weekdays when alarm is triggered. 0 - Mon, 1 - Tue, ... 6 - Sun
        :param duration: Duration of alarm in seconds
        :param volume: Volume to set when alarm is triggered between 0 and 100
        :param station_data: Alarm sound, must be dict:
            - title
            - description
            - thumbnail_url
            - station_url
        :param playlist: Alarm sound, must be iterable returning alarm combatible objects
            - object_type - must be set to tunein_radio
            - object_id - object id
            - title - radio name
        :param enabled: True if alarm should be active, False otherwise
        """
        if time:
            self._time = time
        if weekdays:
            self._weekdays = weekdays
        if duration:
            self._duration = int(duration)
        if volume:
            self._volume = int(volume)
        if station_data:
            self._station_data = station_data
        elif playlist:
            self._station_data = self._get_station_data_from_playlist(playlist)
        elif not self._station_data:
            raise ValueError('Either station_data or playlist must be provided')
        if enabled is not None:
            self._enabled = bool(enabled)

        self._api.set_alarm_info(
            index=self._index,
            hour=int(self._time.split(':')[0]),
            minute=int(self._time.split(':')[1]),
            week=weekday_list_to_hexweek(self._weekdays),
            station_data={
                'title': self._station_data['title'],
                'description': self._station_data['description'],
                'thumbnail': self._station_data['thumbnail_url'],
                'stationurl': self._station_data['station_url'],
            },
            volume=self._volume,
            duration=self._duration)

        self._api.set_alarm_on_off(self._index, 'on' if self._enabled else 'off')

    def delete(self):
        """
        Delete this alarm and set alarm settings to defaults.
        """
        self._api.del_alarm(self._index)
        self._set_defaults()

    def disable(self):
        """
        Disable this alarm.
        """
        self._api.set_alarm_on_off(self._index, 'off')
        self._enabled = False

    def enable(self):
        """
        Enable this alarm.
        """
        self._api.set_alarm_on_off(self._index, 'on')
        self._enabled = True

    def _get_station_data_from_playlist(self, playlist):
        """
        Get station_data by providing playlist of compatible items.

        Playlist items must be an object with following attributes:
        - object_id - object id
        - object_type - must be 'tunein_radio'
        - title - radio name

        :param playlist: Iterable returning alarm combatible objects
        """
        for radio in playlist:
            if radio.object_type not in ['tunein_radio']:
                continue

            station_data = self._api.get_station_data(radio.object_id)
            return {
                'title': station_data['title'] or '',
                'description': station_data['description'] or '',
                'thumbnail_url': station_data['thumbnail'] or '',
                'station_url': station_data['stationurl'] or '',
            }

        raise ValueError('No compatible playlist items. Object type must be tunein_radio.')

    @property
    def index(self):
        """
        :returns: Slot index between 0 and 2
        """
        return self._index

    @property
    def time(self):
        """
        :returns: Alarm trigger time string in HH:MM format
        """
        return self._time

    @property
    def weekdays(self):
        """
        :returns: List of integers representing weekdays when alarm is triggered. 0 - Mon, 1 - Tue, ... 6 - Sun
        """
        return self._weekdays

    @property
    def duration(self):
        """
        :returns: Alarm duration in seconds
        """
        return self._duration

    @property
    def volume(self):
        """
        :returns: Speaker volume when alarm is triggered
        """
        return self._volume

    @property
    def station_data(self):
        """
        :returns: radio station data dict that is used as alarm sound
            - name
            - description
            - thumbnail_url
            - station_url
        """
        return self._station_data

    @property
    def enabled(self):
        """
        :returns: True if alarm is enabled
        """
        return self._enabled


def hexweek_to_weekday_list(hexweek):
    """
    Helper to convert speaker's hex representation of weekdays into list of integers represending weekdays.

    :param hexweek: Hex string .e.g. 0x3E
    :returns: List of weekday integers e.g. [0, 1, 2, 3, 4] for hexweek 0x3E
    """
    intweek = int(hexweek, 16)

    # Mon, Tue, Wed, Thu, Fri, Sat, Sun
    weekday_bits = [32, 16, 8, 4, 2, 1, 64]

    return [weekday for weekday, weekday_bit in enumerate(weekday_bits) if intweek & weekday_bit]


def weekday_list_to_hexweek(weekday_list):
    """
    Helper to convert list of integers represending weekdays into speaker's hex representation of weekdays.

    :param hexweek: List of weekday integers e.g. [0, 1, 2, 3, 4]
    :returns: Hex string .e.g. 0x3E
    """
    # Mon, Tue, Wed, Thu, Fri, Sat, Sun
    weekday_bits = [32, 16, 8, 4, 2, 1, 64]
    weekday_list = set(weekday_list)

    return hex(sum([weekday_bits[weekday] for weekday in weekday_list]))
