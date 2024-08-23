# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from quart.app import QuartClient

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.lookup_user_handler import lookup_user
from nwc_backend.exceptions import (
    InvalidInputException,
    Nip47RequestException,
    NotImplementedException,
)
from nwc_backend.models.nip47_request import ErrorCode, Nip47Request


@patch.object(aiohttp.ClientSession, "get")
async def test_lookup_user_success(mock_get: Mock, test_client: QuartClient) -> None:
    vasp_response = {
        "currencies": [
            {
                "code": "USD",
                "symbol": "$",
                "name": "US Dollar",
                "multiplier": 1000,
                "decimals": 2,
                "min": 1000,
                "max": 1000000,
            }
        ]
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.raise_for_status = Mock()
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
    mock_response = AsyncMock()
    mock_response.raise_for_status = Mock(
        side_effect=aiohttp.ClientResponseError(
            request_info=Mock(), history=(), status=404
        )
    )
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            await lookup_user(
                access_token=token_hex(),
                request=Nip47Request(params={"receiver": {"lud16": "lud16_address"}}),
            )
        assert exc_info.value.error_code == ErrorCode.NOT_FOUND
