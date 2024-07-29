# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from nostr_sdk import Event


class PublishEventFailedException(Exception):
    def __init__(self, event: Event, errors: dict[str, str | None]) -> None:
        super().__init__(f"Publish event {event.as_json()} failed: {str(errors)}")
