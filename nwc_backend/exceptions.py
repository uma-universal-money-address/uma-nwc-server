# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging

from nostr_sdk import ErrorCode, Event
from uma_auth.models.error_response import ErrorResponse


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


class NotImplementedException(Nip47RequestException):
    def __init__(self, error_message: str) -> None:
        super().__init__(
            error_code=ErrorCode.NOT_IMPLEMENTED, error_message=error_message
        )


class VaspErrorResponseException(Nip47RequestException):
    def __init__(self, http_status: int, response: str) -> None:
        try:
            error_response = ErrorResponse.from_json(response)
            super().__init__(
                error_code=ErrorCode[error_response.code],
                error_message=error_response.message,
            )
        except Exception:
            logging.debug(
                "Receive an error response on status %d not in format of ErrorResponse: %s",
                http_status,
                response,
            )
            match http_status:
                case 429:
                    error_code = ErrorCode.RATE_LIMITED
                case 404:
                    error_code = ErrorCode.NOT_FOUND
                case _:
                    error_code = ErrorCode.OTHER
            super().__init__(error_code=error_code, error_message=response)


class ActiveAppConnectionAlreadyExistsException(Exception):
    pass


class AppConnectionNotFoundException(Exception):
    pass
