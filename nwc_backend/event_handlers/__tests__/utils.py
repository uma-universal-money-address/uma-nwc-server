# pyre-strict

from typing import Any, TypeVar

T = TypeVar("T")


def exclude_none_values(dictionary: dict[str, Any]) -> dict[str, Any]:
    return _exclude_none_values_impl(dictionary)


def _exclude_none_values_impl(e: T) -> T:
    if isinstance(e, dict):
        return {k: _exclude_none_values_impl(v) for k, v in e.items() if v is not None}
    elif isinstance(e, list):
        return [_exclude_none_values_impl(i) for i in e]
    else:
        return e
