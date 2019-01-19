import datetime
import unittest
from unittest.mock import MagicMock

from samsung_multiroom.clock import Alarm
from samsung_multiroom.clock import AlarmSlot


def get_alarm():
    api = MagicMock()
    api.get_alarm_info.return_value = [
        {
            '@index': '0',
            'hour': '10',
            'min': '15',
            'week': '0x40',
            'volume': '20',
            'title': None,
            'description': None,
            'thumbnail': None,
            'stationurl': None,
            'set': 'on',
            'soundenable': 'on',
            'sound': '1',
            'alarmsoundname': 'Disco',
            'duration': '10',
        },
        {
            '@index': '1',
            'hour': '8',
            'min': '5',
            'week': '0x3e',
            'volume': '5',
            'title': 'BBC Radio 4',
            'description': 'Intelligent speech',
            'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s25419d.png',
            'stationurl': 'http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls',
            'set': 'on',
            'soundenable': 'off',
            'sound': '-1',
            'alarmsoundname': '',
            'duration': '0',
        }
    ]

    alarm = Alarm(api)

    return (alarm, api)


NOW = datetime.datetime(2018, 1, 7, 15, 45, 32)


class TestAlarm(unittest.TestCase):

    def test_get_slots(self):
        alarm, api = get_alarm()

        slots = alarm.get_slots()

        self.assertEqual(len(slots), 3)

        # 0
        self.assertEqual(slots[0].index, 0)
        self.assertEqual(slots[0].time, '10:15')
        self.assertEqual(slots[0].weekdays, [6]) # Sunday
        self.assertEqual(slots[0].volume, 20)
        self.assertEqual(slots[0].duration, 10)
        self.assertEqual(slots[0].station_data, {
            'title': None,
            'description': None,
            'thumbnail_url': None,
            'station_url': None,
        })
        self.assertTrue(slots[0].enabled)

        # 1
        self.assertEqual(slots[1].index, 1)
        self.assertEqual(slots[1].time, '8:05')
        self.assertEqual(slots[1].weekdays, [0,1,2,3,4]) # Mon-Fri
        self.assertEqual(slots[1].volume, 5)
        self.assertEqual(slots[1].duration, 0)
        self.assertEqual(slots[1].station_data, {
            'title': 'BBC Radio 4',
            'description': 'Intelligent speech',
            'thumbnail_url': 'http://cdn-radiotime-logos.tunein.com/s25419d.png',
            'station_url': 'http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls',
        })
        self.assertTrue(slots[1].enabled)

    def test_set(self):
        alarm, api = get_alarm()

        alarm.slot(2).set(
            time='7:12',
            weekdays=[5, 6], # Sat,Sun
            station_data={
                'title': 'BBC Radio 4',
                'description': 'Intelligent speech',
                'thumbnail_url': 'http://cdn-radiotime-logos.tunein.com/s25419d.png',
                'station_url': 'http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls',
            },
            enabled=True,
        )

        api.set_alarm_info.assert_called_once_with(
            index=2,
            hour=7,
            minute=12,
            week='0x41',
            duration=0,
            volume=5,
            station_data={
                'title': 'BBC Radio 4',
                'description': 'Intelligent speech',
                'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s25419d.png',
                'stationurl': 'http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls',
            }
        )
        api.set_alarm_on_off.assert_called_once_with(2, 'on')

    def test_set_from_playlist(self):
        alarm, api = get_alarm()

        api.get_station_data.return_value = {
            'cpname': 'TuneIn',
            'browsemode': '0',
            'title': 'BBC Radio 4',
            'description': 'Intelligent speech',
            'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s25419d.png',
            'stationurl': 'http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls',
            'timestamp': '2019-01-08T15:21:47Z',
        }

        playlist = [
            type('Item', (object, ), {
                'object_type': 'unsupported_type',
                'object_id': 1,
                'name': 'Some audio'
            }),
            type('Item', (object, ), {
                'object_type': 'tunein_radio',
                'object_id': 20,
                'name': 'Some radio'
            }),
            type('Item', (object, ), {
                'object_type': 'tunein_radio',
                'object_id': 21,
                'name': 'Some other radio'
            })
        ]

        alarm.slot(2).set(
            time='7:12',
            weekdays=[5, 6], # Sat,Sun
            playlist=playlist,
            enabled=True,
        )

        api.set_alarm_info.assert_called_once_with(
            index=2,
            hour=7,
            minute=12,
            week='0x41',
            duration=0,
            volume=5,
            station_data={
                'title': 'BBC Radio 4',
                'description': 'Intelligent speech',
                'thumbnail': 'http://cdn-radiotime-logos.tunein.com/s25419d.png',
                'stationurl': 'http://opml.radiotime.com/Tune.ashx?id=s25419&partnerId=qDDAbg6M&serial=90F1AAD31D82&formats=mp3,wma,aac,qt,hls',
            }
        )
        api.set_alarm_on_off.assert_called_once_with(2, 'on')

    @unittest.mock.patch('datetime.datetime')
    def test_delete(self, dt):
        alarm, api = get_alarm()

        dt.now.return_value = NOW

        slots = alarm.get_slots()
        slots[0].delete()

        self.assertEqual(slots[0].index, 0)
        self.assertEqual(slots[0].time, '15:45')
        self.assertEqual(slots[0].weekdays, [NOW.weekday()])
        self.assertEqual(slots[0].volume, 5)
        self.assertEqual(slots[0].duration, 0)
        self.assertEqual(slots[0].station_data, None)
        self.assertFalse(slots[0].enabled)

        api.del_alarm.assert_called_once_with(0)

    def test_disable(self):
        alarm, api = get_alarm()

        slots = alarm.get_slots()
        slots[0].disable()

        self.assertFalse(slots[0].enabled)
        api.set_alarm_on_off.assert_called_once_with(0, 'off')

    def test_enable(self):
        alarm, api = get_alarm()

        slots = alarm.get_slots()
        slots[0].enable()

        self.assertTrue(slots[0].enabled)
        api.set_alarm_on_off.assert_called_once_with(0, 'on')
