# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
from quart.app import QuartClient

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.get_info_handler import get_info
from nwc_backend.models.__tests__.model_examples import create_currency
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.nip47_request_method import Nip47RequestMethod


@patch.object(aiohttp.ClientSession, "get")
async def test_get_info_success(mock_get: Mock, test_client: QuartClient) -> None:
    vasp_response = {
        "pubkey": token_hex(),
        "network": "mainnet",
        "methods": [
            Nip47RequestMethod.FETCH_QUOTE.value,
            Nip47RequestMethod.EXECUTE_QUOTE.value,
        ],
        "lud16": "$alice@uma.me",
        "currencies": [
            {
                "currency": create_currency("USD").to_dict(),
                "multiplier": 15351.4798,
                "min": 1,
                "max": 1000_00,
            }
        ],
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_get.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        response = await get_info(
            access_token=token_hex(),
            request=Nip47Request(params={}),
        )

        mock_get.assert_called_once_with(url="/info", params=None, headers=ANY)
        assert exclude_none_values(response.to_dict()) == vasp_response
