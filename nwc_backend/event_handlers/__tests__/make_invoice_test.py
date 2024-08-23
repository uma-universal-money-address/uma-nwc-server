# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from pydantic_core import ValidationError
from quart.app import QuartClient
from uma_auth.models.make_invoice_request import MakeInvoiceRequest
from uma_auth.models.transaction import TransactionType

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.make_invoice_handler import make_invoice
from nwc_backend.models.nip47_request import Nip47Request


@patch.object(aiohttp.ClientSession, "post")
async def test_make_invoice_success(mock_post: Mock, test_client: QuartClient) -> None:
    vasp_response = {
        "type": TransactionType.INCOMING.value,
        "invoice": "lnbcrt1u1pjd4dnypp556q6aag8hf6rweejfdv8tp2v4034jdfvxj8p94rr2fwgvuy8xxxqsp5cqyc3alzjf3ua6up2jpvfu9xqa8rjk5txpeh3jhvcm2h8xprk8kqxqyz5vqnp4qga909cwg8hfr95yqftg6k7a99cm5f8xpzuven6680l0vancdhyjvcqzpgdqq9qyyssq2tcyjf6l4at69ljxnk8wcnx20s3qn2k356pn86qjah83ym3dhg4n48ukdmw79axgtd4fj6e9cezjyyca7m28q2flcj2wua0an5434dgppwa0mv",
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "payment_hash": "a681aef507ba743767324b5875854cabe359352c348e12d463525c867087318c",
        "amount": 100000,
        "created_at": 1692055140,
        "expires_at": 1692141540,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_post.return_value.__aenter__.return_value = mock_response

    params = {"amount": 100000, "expiry": 86400}
    async with test_client.app.app_context():
        response = await make_invoice(
            access_token=token_hex(),
            request=Nip47Request(params=params),
        )

        mock_post.assert_called_once_with(
            url="/invoice",
            data=MakeInvoiceRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        assert exclude_none_values(response.to_dict()) == vasp_response


async def test_execute_quote_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(ValidationError):
            await make_invoice(
                access_token=token_hex(),
                request=Nip47Request(params={"amount": -1000}),
            )
