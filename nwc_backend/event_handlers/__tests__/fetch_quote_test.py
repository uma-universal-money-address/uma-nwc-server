# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.fetch_quote_handler import fetch_quote
from nwc_backend.exceptions import InvalidInputException, NotImplementedException
from nwc_backend.models.nip47_request import Nip47Request


@patch.object(aiohttp.ClientSession, "get")
async def test_fetch_quote_success(mock_get: Mock) -> None:
    now = datetime.now(timezone.utc)
    vasp_response = {
        "sending_currency_code": "SAT",
        "receiving_currency_code": "USD",
        "payment_hash": token_hex(),
        "expires_at": int((now + timedelta(minutes=5)).timestamp()),
        "multiplier": 15351.4798,
        "fees": 10,
        "total_sending_amount": 1_000_000,
        "total_receiving_amount": 65,
        "created_at": int(now.timestamp()),
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.raise_for_status = Mock()
    mock_get.return_value.__aenter__.return_value = mock_response

    receiver_address = "$alice@uma.me"
    params = {
        "receiver": {"lud16": receiver_address},
        "sending_currency_code": "SAT",
        "receiving_currency_code": "USD",
        "locked_currency_amount": 1_000_000,
        "locked_currency_side": "sending",
    }
    quote = await fetch_quote(
        access_token=token_hex(),
        request=Nip47Request(params=params),
    )

    params.pop("receiver")
    params["receiver_address"] = receiver_address
    mock_get.assert_called_once_with(url="/quote/lud16", params=params, headers=ANY)

    assert exclude_none_values(quote.to_dict()) == vasp_response


async def test_fetch_quote_failure__invalid_input() -> None:
    with pytest.raises(InvalidInputException):
        await fetch_quote(
            access_token=token_hex(),
            request=Nip47Request(
                params={
                    "receiver": {"lud16": "$alice@uma.me"},
                    "sending_currency_code": "SAT",
                    "receiving_currency_code": "USD",
                    "locked_currency_amount": 1_000_000,
                    "locked_currency_side": "send",  # wrong enum value
                }
            ),
        )


async def test_fetch_quote_failure__unsupported_bolt12() -> None:
    with pytest.raises(NotImplementedException):
        await fetch_quote(
            access_token=token_hex(),
            request=Nip47Request(
                params={
                    "receiver": {"bolt12": "$alice@uma.me"},  # bolt12 not supported
                    "sending_currency_code": "SAT",
                    "receiving_currency_code": "USD",
                    "locked_currency_amount": 1_000_000,
                    "locked_currency_side": "sending",
                }
            ),
        )
