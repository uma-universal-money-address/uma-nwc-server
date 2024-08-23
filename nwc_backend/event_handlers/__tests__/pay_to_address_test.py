# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from pydantic_core import ValidationError
from quart.app import QuartClient
from uma_auth.models.pay_to_address_request import PayToAddressRequest

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.pay_to_address_handler import pay_to_address
from nwc_backend.exceptions import InvalidInputException, Nip47RequestException
from nwc_backend.models.nip47_request import ErrorCode, Nip47Request


@patch.object(aiohttp.ClientSession, "post")
async def test_pay_to_address_success(
    mock_post: Mock, test_client: QuartClient
) -> None:
    now = datetime.now(timezone.utc)
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "quote": {
            "sending_currency_code": "SAT",
            "receiving_currency_code": "USD",
            "payment_hash": token_hex(),
            "expires_at": int((now + timedelta(minutes=5)).timestamp()),
            "multiplier": 15351.4798,
            "fees": 10,
            "total_sending_amount": 1_000_000,
            "total_receiving_amount": 65,
            "created_at": int(now.timestamp()),
        },
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.raise_for_status = Mock()
    mock_post.return_value.__aenter__.return_value = mock_response

    params = {
        "receiver": {"lud16": "$alice@uma.me"},
        "sending_currency_code": "SAT",
        "sending_currency_amount": 1_000_000,
    }
    async with test_client.app.app_context():
        response = await pay_to_address(
            access_token=token_hex(),
            request=Nip47Request(params=params),
        )

        params["receiver_address"] = params.pop("receiver")["lud16"]  # pyre-ignore[16]
        mock_post.assert_called_once_with(
            url="/payments/lud16",
            data=PayToAddressRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        assert exclude_none_values(response.to_dict()) == vasp_response


async def test_pay_to_address_failure__no_receiver(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await pay_to_address(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "sending_currency_code": "SAT",
                        "sending_currency_amount": 1_000_000,
                    }
                ),
            )


async def test_pay_to_address_failure__multiple_receivers(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await pay_to_address(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "receiver": {
                            "lud16": "$alice@uma.me",
                            "bolt12": "lno1qqszqfnjxapqxqrrzd9hxyarjwpzqarhdaexgmm9wejkgtm9venj2cmyde3x7urpwp8xgetr5fpqqg5w",
                        },
                        "sending_currency_code": "SAT",
                        "sending_currency_amount": 1_000_000,
                    }
                ),
            )


async def test_pay_to_address_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(ValidationError):
            await pay_to_address(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "receiver": {"lud16": "$alice@uma.me"},
                        "sending_currency_code": "SAT",
                        "sending_currency_amount": "amount",  # should be integer
                    }
                ),
            )


@patch.object(aiohttp.ClientSession, "post")
async def test_pay_to_address_failure__http_raises(
    mock_post: Mock, test_client: QuartClient
) -> None:
    mock_response = AsyncMock()
    mock_response.raise_for_status = Mock(
        side_effect=aiohttp.ClientResponseError(request_info=Mock(), history=())
    )
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            await pay_to_address(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "receiver": {"lud16": "$alice@uma.me"},
                        "sending_currency_code": "SAT",
                        "sending_currency_amount": 1_000_000,
                    }
                ),
            )
            assert exc_info.value.error_code == ErrorCode.PAYMENT_FAILED
