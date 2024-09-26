# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from quart.app import QuartClient
from uma_auth.models.error_response import ErrorCode as VaspErrorCode
from uma_auth.models.error_response import ErrorResponse as VaspErrorResponse

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.lookup_user_handler import lookup_user
from nwc_backend.exceptions import (
    InvalidInputException,
    Nip47RequestException,
    NotImplementedException,
)
from nwc_backend.models.__tests__.model_examples import create_currency
from nwc_backend.models.nip47_request import ErrorCode, Nip47Request


@patch.object(aiohttp.ClientSession, "get")
async def test_lookup_user_success(mock_get: Mock, test_client: QuartClient) -> None:
    vasp_response = {
        "currencies": [
            {
                "currency": create_currency("USD").to_dict(),
                "multiplier": 1000,
                "min": 1000,
                "max": 1000000,
            }
        ]
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_get.return_value.__aenter__.return_value = mock_response

    receiver_address = "$alice@vasp.net"
    params = {
        "receiver": {"lud16": receiver_address},
        "base_sending_currency_code": "USD",
    }
    async with test_client.app.app_context():
        response = await lookup_user(
            access_token=token_hex(),
            request=Nip47Request(params=params),
        )

        params.pop("receiver")
        mock_get.assert_called_once_with(
            url=f"/receiver/lud16/{receiver_address}", params=params, headers=ANY
        )
        assert exclude_none_values(response.to_dict()) == vasp_response


async def test_lookup_user_failure__missing_receiver(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await lookup_user(
                access_token=token_hex(),
                request=Nip47Request(params={}),
            )


async def test_lookup_user_failure__multiple_receivers(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await lookup_user(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "receiver": {
                            "bolt12": "bolt12_address",
                            "lud16": "lud16_address",
                        }
                    }
                ),
            )


async def test_lookup_user_failure__unsupported_bolt12(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(NotImplementedException):
            await lookup_user(
                access_token=token_hex(),
                request=Nip47Request(params={"receiver": {"bolt12": "bolt12_address"}}),
            )


@patch.object(aiohttp.ClientSession, "get")
async def test_lookup_user_failure__not_found(
    mock_post: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {"code": VaspErrorCode.NOT_FOUND.name, "message": "User not found."}
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            await lookup_user(
                access_token=token_hex(),
                request=Nip47Request(params={"receiver": {"lud16": "lud16_address"}}),
            )
        assert exc_info.value.error_code == ErrorCode.NOT_FOUND
