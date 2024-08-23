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
from nwc_backend.event_handlers.execute_quote_handler import execute_quote
from nwc_backend.exceptions import InvalidInputException, Nip47RequestException
from nwc_backend.models.nip47_request import ErrorCode, Nip47Request


@patch.object(aiohttp.ClientSession, "post")
async def test_execute_quote_success(mock_post: Mock, test_client: QuartClient) -> None:
    vasp_response = {"preimage": token_hex()}
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
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
    vasp_response = VaspErrorResponse.from_dict(
        {"code": VaspErrorCode.PAYMENT_FAILED.name, "message": "No route."}
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            await execute_quote(
                access_token=token_hex(),
                request=Nip47Request(params={"payment_hash": token_hex()}),
            )
            assert exc_info.value.error_code == ErrorCode.PAYMENT_FAILED
            assert exc_info.value.error_message == vasp_response.message
