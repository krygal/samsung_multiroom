"""Event dispatching."""
import fnmatch


class EventLoop:
    """
    Listen to speaker events.

    Use add_listener to subscribe to events of particular type.
    """

    def __init__(self, api_stream):
        """
        :param api_stream: ApiStream instance
        """
        self._api_stream = api_stream
        self._listeners = []
        self._factories = _get_default_factories()

    def register_factory(self, factory):
        """
        Register event factory function.

        :param factory: Callable accepting ApiResponse instance
        """
        if not callable(factory):
            raise ValueError('factory must be callable')

        self._factories.append(factory)

    def add_listener(self, event_name, listener):
        """
        :param event_name: Event name. See Events for all supported events
        :param listener: Callable. Will be called on a matching event and passed matching Event object
        """
        if not callable(listener):
            raise ValueError('listener must be a callable')

        self._listeners.append((event_name, listener))

    async def loop(self):
        """
        Start emitting speaker events.
        """
        for response in self._api_stream.open('/UIC?cmd=%3Cname%3EGetMainInfo%3C/name%3E'):
            event = self._factory(response)
            if event:
                self._dispatch_event(event)

    def _dispatch_event(self, event):
        for event_name, listener in self._listeners:
            if fnmatch.fnmatch(event.name, event_name):
                listener(event)

    def _factory(self, response):
        """
        Factory event from response.

        :param response: ApiResponse instance
        """
        for factory in reversed(self._factories):
            event = factory(response)

            if event:
                return event

        return None


def _get_default_factories():
    event_classes = [
        ('samsung_multiroom.event.type.speaker_mute_changed', 'SpeakerMuteChangedEvent'),
        ('samsung_multiroom.event.type.speaker_player', 'SpeakerPlayerEvent'),
        ('samsung_multiroom.event.type.speaker_player_repeat_changed', 'SpeakerPlayerRepeatChangedEvent'),
        ('samsung_multiroom.event.type.speaker_player_shuffle_changed', 'SpeakerPlayerShuffleChangedEvent'),
        ('samsung_multiroom.event.type.speaker_service', 'SpeakerServiceEvent'),
        ('samsung_multiroom.event.type.speaker_volume_changed', 'SpeakerVolumeChangedEvent'),
    ]

    factories = []

    for module_name, class_name in event_classes:
        mod = __import__(module_name, fromlist=[class_name])
        klass = getattr(mod, class_name)

        factories.append(klass.factory)

    return factories
