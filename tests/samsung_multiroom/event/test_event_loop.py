import unittest
from unittest.mock import MagicMock

import pytest

from samsung_multiroom.api import ApiResponse
from samsung_multiroom.event import EventLoop
from samsung_multiroom.event.event import Event


def _get_event_loop():
    api_stream = MagicMock()

    event_loop = EventLoop(api_stream)

    return (event_loop, api_stream)


def _fake_event_factory(response):
    event = MagicMock(spec=Event)
    event.name = 'fake.event'
    return event


def _get_api_response(name):
    event = MagicMock(spec=ApiResponse)
    event.name = name
    return event


class TestEventLoop():  # pytest-asyncio doesn't play well with unittest.TestCase

    @pytest.mark.asyncio
    async def test_loop(self):
        listener = MagicMock()

        event_loop, api_stream = _get_event_loop()

        api_stream.open.return_value = iter([
            _get_api_response('FakeEvent'),
        ])

        event_loop.register_factory(_fake_event_factory)
        event_loop.add_listener('fake.event', listener)

        await event_loop.loop()

        listener.assert_called_once()

    @pytest.mark.asyncio
    async def test_loop_no_events(self):
        listener = MagicMock()

        event_loop, api_stream = _get_event_loop()

        api_stream.open.return_value = iter([
            _get_api_response('FakeEvent'),
        ])

        event_loop.add_listener('*', listener)

        await event_loop.loop()

        listener.assert_not_called()
