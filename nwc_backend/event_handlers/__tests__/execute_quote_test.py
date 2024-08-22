# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from quart.app import QuartClient

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.execute_quote_handler import execute_quote
from nwc_backend.exceptions import InvalidInputException, Nip47RequestException
from nwc_backend.models.nip47_request import ErrorCode, Nip47Request


@patch.object(aiohttp.ClientSession, "post")
async def test_execute_quote_success(mock_post: Mock, test_client: QuartClient) -> None:
    vasp_response = {"preimage": token_hex()}
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.raise_for_status = Mock()
    mock_post.return_value.__aenter__.return_value = mock_response

    payment_hash = token_hex()
    async with test_client.app.app_context():
        response = await execute_quote(
            access_token=token_hex(),
            request=Nip47Request(params={"payment_hash": payment_hash}),
        )
    mock_post.assert_called_once_with(
        url=f"/quote/{payment_hash}", data=None, headers=ANY
    )
    assert exclude_none_values(response.to_dict()) == vasp_response


async def test_execute_quote_failure__invalid_input(test_client: QuartClient) -> None:
    with pytest.raises(InvalidInputException):
        async with test_client.app.app_context():
            await execute_quote(
                access_token=token_hex(),
                request=Nip47Request(params={"payment_hashh": token_hex()}),
            )


@patch.object(aiohttp.ClientSession, "post")
async def test_execute_quote_failure__http_raises(
    mock_post: Mock, test_client: QuartClient
) -> None:
    mock_response = AsyncMock()
    mock_response.raise_for_status = Mock(
        side_effect=aiohttp.ClientResponseError(request_info=Mock(), history=())
    )
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            await execute_quote(
                access_token=token_hex(),
                request=Nip47Request(params={"payment_hash": token_hex()}),
            )
    assert exc_info.value.error_code == ErrorCode.PAYMENT_FAILED
