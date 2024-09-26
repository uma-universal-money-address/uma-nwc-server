# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from typing import Any, Optional
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from quart.app import QuartClient

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.get_balance_handler import get_balance
from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.__tests__.model_examples import create_currency
from nwc_backend.models.nip47_request import Nip47Request


@patch.object(aiohttp.ClientSession, "get")
@pytest.mark.parametrize(
    "currency_code",
    ["USD", None],
)
async def test_get_balance_success(
    mock_get: Mock, currency_code: Optional[str], test_client: QuartClient
) -> None:
    vasp_response: dict[str, Any] = {"balance": 1_000_000}
    if currency_code:
        vasp_response["currency"] = create_currency(currency_code).to_dict()

    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_get.return_value.__aenter__.return_value = mock_response

    params = {}
    if currency_code:
        params["currency_code"] = currency_code

    async with test_client.app.app_context():
        response = await get_balance(
            access_token=token_hex(),
            request=Nip47Request(params=params),
        )

        mock_get.assert_called_once_with(
            url="/balance", params=params if params else None, headers=ANY
        )
        assert exclude_none_values(response.to_dict()) == vasp_response


async def test_get_balance_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await get_balance(
                access_token=token_hex(),
                request=Nip47Request(params={"currency_code": 123}),  # wrong value
            )
