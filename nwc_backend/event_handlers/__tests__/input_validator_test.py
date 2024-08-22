# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Any, Type

import pytest
from uma_auth.models.locked_currency_side import LockedCurrencySide

from nwc_backend.event_handlers.input_validator import (
    get_optional_field,
    get_required_field,
)
from nwc_backend.exceptions import InvalidInputException


async def test_get_required_field__succeeded() -> None:
    params = {
        "locked_currency_side": LockedCurrencySide.SENDING.value,
        "currency": "USD",
        "amount": 1,
    }
    locked_currency_side = get_required_field(
        params, "locked_currency_side", LockedCurrencySide
    )
    assert isinstance(locked_currency_side, LockedCurrencySide)

    currency = get_required_field(params, "currency", str)
    assert isinstance(currency, str)

    amount = get_required_field(params, "amount", int)
    assert isinstance(amount, int)


@pytest.mark.parametrize(
    "params, field_name, expected_type",
    [
        (
            {"locked_currency_side": "send"},  # invalid enum value
            "locked_currency_side",
            LockedCurrencySide,
        ),
        ({"amount": 10}, "amount", str),  # invalid type
        ({"amount": 10}, "receiver", str),  # required field not exists
    ],
)
async def test_get_required_field__failed(
    params: dict[str, Any], field_name: str, expected_type: Type[Any]  # pyre-ignore[2]
) -> None:
    with pytest.raises(InvalidInputException):
        get_required_field(params, field_name, expected_type)


async def test_get_optional_field__succeeded() -> None:
    params = {
        "locked_currency_side": LockedCurrencySide.SENDING.value,
        "currency": "USD",
        "amount": 1,
    }
    locked_currency_side = get_optional_field(
        params, "locked_currency_side", LockedCurrencySide
    )
    assert isinstance(locked_currency_side, LockedCurrencySide)

    currency = get_optional_field(params, "currency", str)
    assert isinstance(currency, str)

    amount = get_optional_field(params, "amount", int)
    assert isinstance(amount, int)

    pubkey = get_optional_field(params, "pubkey", str)
    assert pubkey is None


@pytest.mark.parametrize(
    "params, field_name, expected_type",
    [
        (
            {"locked_currency_side": "send"},  # invalid enum value
            "locked_currency_side",
            LockedCurrencySide,
        ),
        ({"amount": 10}, "amount", str),  # invalid type
    ],
)
async def test_get_optional_field__failed(
    params: dict[str, Any], field_name: str, expected_type: Type[Any]  # pyre-ignore[2]
) -> None:
    with pytest.raises(InvalidInputException):
        get_optional_field(params, field_name, expected_type)
