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
from uma_auth.models.transaction import TransactionType

from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.lookup_invoice_handler import lookup_invoice
from nwc_backend.exceptions import (
    ErrorCode,
    InvalidInputException,
    Nip47RequestException,
)
from nwc_backend.models.nip47_request import Nip47Request

INVOICE = "lnbcrt1u1pjd4dnypp556q6aag8hf6rweejfdv8tp2v4034jdfvxj8p94rr2fwgvuy8xxxqsp5cqyc3alzjf3ua6up2jpvfu9xqa8rjk5txpeh3jhvcm2h8xprk8kqxqyz5vqnp4qga909cwg8hfr95yqftg6k7a99cm5f8xpzuven6680l0vancdhyjvcqzpgdqq9qyyssq2tcyjf6l4at69ljxnk8wcnx20s3qn2k356pn86qjah83ym3dhg4n48ukdmw79axgtd4fj6e9cezjyyca7m28q2flcj2wua0an5434dgppwa0mv"
PAYMENT_HASH = "a681aef507ba743767324b5875854cabe359352c348e12d463525c867087318c"


@patch.object(aiohttp.ClientSession, "get")
@pytest.mark.parametrize(
    "params",
    [{"payment_hash": PAYMENT_HASH}, {"invoice": INVOICE}],
)
async def test_lookup_invoice_success(
    mock_get: Mock, params: dict[str, str], test_client: QuartClient
) -> None:
    vasp_response = {
        "type": TransactionType.INCOMING.value,
        "invoice": INVOICE,
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "payment_hash": PAYMENT_HASH,
        "amount": 100000,
        "created_at": 1692055140,
        "expires_at": 1692141540,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_get.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        invoice = await lookup_invoice(
            access_token=token_hex(),
            request=Nip47Request(params=params),
        )

        mock_get.assert_called_once_with(
            url=f"/invoices/{PAYMENT_HASH}", params=None, headers=ANY
        )
        assert exclude_none_values(invoice.to_dict()) == vasp_response


async def test_lookup_invoice_failure__neither_provided(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await lookup_invoice(
                access_token=token_hex(),
                request=Nip47Request(params={}),
            )


async def test_lookup_invoice_failure__both_provided(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await lookup_invoice(
                access_token=token_hex(),
                request=Nip47Request(
                    params={"payment_hash": PAYMENT_HASH, "invoice": INVOICE}
                ),
            )


async def test_lookup_invoice_failure__invalid_invoice(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            await lookup_invoice(
                access_token=token_hex(),
                request=Nip47Request(
                    params={
                        "invoice": "lnbcrt1u1pjd4dnypp556q6aag8hf6rweejfdv8tp2v4034jdfvxj8p94rr2fwgvuy8xxxqsp5cqyc3alzjf3ua6up2jpvfu9xqa8rjk5txpeh3jhvcm2h8xprk8kqxqyz5vqnp4qga909cwg8hfr95yqftg6k7a99cm5f8xpzuven6680l0vancdhyjvcqzpgdqq9qyyssq2tcyjf6l4at69ljxnk8wcnx20s3qn2k"
                    }
                ),
            )


@patch.object(aiohttp.ClientSession, "get")
async def test_lookup_invoice_failure__not_found(
    mock_post: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {"code": VaspErrorCode.NOT_FOUND.name, "message": "Invoice not found."}
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            await lookup_invoice(
                access_token=token_hex(),
                request=Nip47Request(params={"payment_hash": PAYMENT_HASH}),
            )
            assert exc_info.value.error_code == ErrorCode.NOT_FOUND
            assert exc_info.value.error_message == vasp_response.message
