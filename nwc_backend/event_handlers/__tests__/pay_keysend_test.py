# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from pydantic_core import ValidationError
from quart.app import QuartClient
from uma_auth.models.pay_keysend_request import PayKeysendRequest

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.pay_keysend_handler import pay_keysend
from nwc_backend.exceptions import Nip47RequestException
from nwc_backend.models.nip47_request import ErrorCode, Nip47Request


@patch.object(aiohttp.ClientSession, "post")
async def test_pay_keysend_success(mock_post: Mock, test_client: QuartClient) -> None:
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.raise_for_status = Mock()
    mock_post.return_value.__aenter__.return_value = mock_response

    params = {
        "pubkey": token_hex(),
        "amount": 10000,
        "tlv_records": [{"type": 5482373484, "value": "0123456789abcdef"}],
    }
    async with test_client.app.app_context():
        response = await pay_keysend(
            access_token=token_hex(),
            request=Nip47Request(params=params),
        )

        mock_post.assert_called_once_with(
            url="/payments/keysend",
            data=PayKeysendRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        assert exclude_none_values(response.to_dict()) == vasp_response


async def test_pay_keysend_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(ValidationError):
            await pay_keysend(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "pubkey": token_hex(),
                        "amount": "abc",
                    }
                ),
            )


@patch.object(aiohttp.ClientSession, "post")
async def test_pay_keysend_failure__http_raises(
    mock_post: Mock, test_client: QuartClient
) -> None:
    mock_response = AsyncMock()
    mock_response.raise_for_status = Mock(
        side_effect=aiohttp.ClientResponseError(request_info=Mock(), history=())
    )
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            await pay_keysend(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "pubkey": token_hex(),
                        "amount": 10000,
                    }
                ),
            )
        assert exc_info.value.error_code == ErrorCode.PAYMENT_FAILED
