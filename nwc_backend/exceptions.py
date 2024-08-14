# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from nostr_sdk import ErrorCode, Event


class PublishEventFailedException(Exception):
    def __init__(self, event: Event, errors: dict[str, str | None]) -> None:
        super().__init__(f"Publish event {event.as_json()} failed: {str(errors)}")


class EventBuilderException(Exception):
    pass


class InvalidClientIdException(Exception):
    pass


class Nip47RequestException(Exception):
    def __init__(self, error_code: ErrorCode, error_message: str) -> None:
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(error_message)


class InvalidInputException(Nip47RequestException):
    def __init__(self, error_message: str) -> None:
        super().__init__(error_code=ErrorCode.OTHER, error_message=error_message)
