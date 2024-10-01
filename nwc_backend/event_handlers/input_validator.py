# pyre-strict

from enum import Enum
from typing import Any, Optional, Type, TypeVar

from nwc_backend.exceptions import InvalidInputException

T = TypeVar("T")


def get_required_field(
    params: dict[str, Any], field_name: str, expected_type: Type[T]
) -> T:
    if field_name not in params:
        raise InvalidInputException(f"Required param {field_name} not found.")

    return _ensure_type(field_name, params[field_name], expected_type)


def get_optional_field(
    params: dict[str, Any], field_name: str, expected_type: Type[T]
) -> Optional[T]:
    if field_name not in params:
        return None
    return _ensure_type(field_name, params[field_name], expected_type)


def _ensure_type(
    field_name: str, value: Any, expected_type: Type[T]  # pyre-ignore[2]
) -> T:
    if issubclass(expected_type, Enum):
        if not isinstance(value, str):
            raise InvalidInputException(
                f"Expect {field_name} to have one of the values in {[e.value for e in expected_type]}, {value} found."  # pyre-ignore[16]
            )
        try:
            return expected_type(value.lower())  # pyre-ignore[19]
        except ValueError:
            raise InvalidInputException(
                f"Expect {field_name} to have one of the values in {[e.value for e in expected_type]}, {value} found."
            )

    if not isinstance(value, expected_type):
        raise InvalidInputException(
            f"Expect {field_name} to have type {expected_type}, {type(value)} found."
        )
    return value
