# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from quart.app import QuartClient
from uma_auth.models.transaction import TransactionType

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.list_transactions_handler import list_transactions
from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request


@patch.object(aiohttp.ClientSession, "get")
async def test_list_transactions_success(
    mock_get: Mock, test_client: QuartClient
) -> None:
    vasp_response = {
        "transactions": [
            {
                "type": TransactionType.INCOMING.value,
                "invoice": token_hex(),
                "preimage": token_hex(),
                "payment_hash": token_hex(),
                "amount": 100000,
                "created_at": 1692055140,
                "expires_at": 1692141540,
            },
            {
                "type": TransactionType.OUTGOING.value,
                "invoice": token_hex(),
                "preimage": token_hex(),
                "payment_hash": token_hex(),
                "amount": 50000,
                "created_at": 1692024140,
                "fees_paid": 20,
            },
        ]
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.raise_for_status = Mock()
    mock_get.return_value.__aenter__.return_value = mock_response

    params = {"from": 1691024140, "limit": 50, "offset": 100}
    async with test_client.app.app_context():
        invoice = await list_transactions(
            access_token=token_hex(),
            request=Nip47Request(params=params),
        )

        mock_get.assert_called_once_with(
            url="/transactions", params=params, headers=ANY
        )
        assert exclude_none_values(invoice.to_dict()) == vasp_response


async def test_list_transactions_failure__invalid_input(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await list_transactions(
                access_token=token_hex(),
                request=Nip47Request(
                    params={"from": "abcde", "limit": 50, "offset": 100}
                ),
            )
