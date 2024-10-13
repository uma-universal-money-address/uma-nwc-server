from typing import Any, Callable, Coroutine, List

from nostr_sdk import Client
from nostr_sdk.nostr_ffi import Event, Filter
from nostr_sdk.nostr_sdk_ffi import EventSource, Output, SendEventOutput


class FakeNostrClient(Client):
    def __init__(self, *args, **kwargs):
        self.connected = False
        self.sent_events = []
        self.last_filters = []
        self.added_relays: List[str] = []
        self.on_get_events: Callable[
            [List[Filter], EventSource], Coroutine[Any, Any, List[Event]]
        ] = None

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    async def add_relay(self, url: str) -> bool:
        self.added_relays.append(url)
        return True

    async def add_read_relay(self, url: str) -> bool:
        self.added_relays.append(url)
        return True

    async def get_events_of(
        self, filters: List[Filter], source: EventSource
    ) -> List[Event]:
        self.last_filters = filters
        if self.on_get_events:
            return await self.on_get_events(filters, source)
        return []

    async def send_event(self, event: Event) -> SendEventOutput:
        self.sent_events.append(event)
        return SendEventOutput(
            id=event.id(),
            output=Output(success=self.added_relays, failed={}),
        )
