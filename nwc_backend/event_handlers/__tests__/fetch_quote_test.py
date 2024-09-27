# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from quart.app import QuartClient

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.fetch_quote_handler import fetch_quote
from nwc_backend.exceptions import InvalidInputException, NotImplementedException
from nwc_backend.models.__tests__.model_examples import (
    create_currency,
    create_nip47_request,
)
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.payment_quote import PaymentQuote


@patch.object(aiohttp.ClientSession, "get")
async def test_fetch_quote_success(mock_get: Mock, test_client: QuartClient) -> None:
    now = datetime.now(timezone.utc)
    payment_hash = token_hex()
    vasp_response = {
        "sending_currency": create_currency("SAT").to_dict(),
        "receiving_currency": create_currency("USD").to_dict(),
        "payment_hash": payment_hash,
        "expires_at": int((now + timedelta(minutes=5)).timestamp()),
        "multiplier": 15351.4798,
        "fees": 10,
        "total_sending_amount": 1_000_000,
        "total_receiving_amount": 65,
        "created_at": int(now.timestamp()),
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_get.return_value.__aenter__.return_value = mock_response

    receiver_address = "$alice@uma.me"
    params = {
        "receiver": {"lud16": receiver_address},
        "sending_currency_code": "SAT",
        "receiving_currency_code": "USD",
        "locked_currency_amount": 1_000_000,
        "locked_currency_side": "sending",
    }
    async with test_client.app.app_context():
        request = await create_nip47_request(params=params)
        quote = await fetch_quote(
            access_token=token_hex(),
            request=request,
        )

        params.pop("receiver")
        params["receiver_address"] = receiver_address
        mock_get.assert_called_once_with(url="/quote/lud16", params=params, headers=ANY)
        assert exclude_none_values(quote.to_dict()) == vasp_response

        stored_quote = await PaymentQuote.from_payment_hash(payment_hash=payment_hash)
        assert stored_quote
        assert stored_quote.sending_currency_code == quote.sending_currency.code
        assert stored_quote.sending_currency_amount == quote.total_sending_amount
        assert stored_quote.receiver_address == receiver_address


async def test_fetch_quote_failure__no_receivers(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await fetch_quote(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "sending_currency_code": "SAT",
                        "receiving_currency_code": "USD",
                        "locked_currency_amount": 1_000_000,
                        "locked_currency_side": "sending",
                    }
                ),
            )


async def test_fetch_quote_failure__multiple_receivers(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await fetch_quote(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "receiver": {
                            "lud16": "$alice@uma.me",
                            "bolt12": "lno1qqszqfnjxapqxqrrzd9hxyarjwpzqarhdaexgmm9wejkgtm9venj2cmyde3x7urpwp8xgetr5fpqqg5w",
                        },
                        "sending_currency_code": "SAT",
                        "receiving_currency_code": "USD",
                        "locked_currency_amount": 1_000_000,
                        "locked_currency_side": "sending",
                    }
                ),
            )


async def test_fetch_quote_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
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


async def test_fetch_quote_failure__unsupported_bolt12(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
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
