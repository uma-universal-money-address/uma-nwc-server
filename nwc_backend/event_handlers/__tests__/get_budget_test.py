# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from nostr_sdk import ErrorCode
from quart.app import QuartClient
from sqlalchemy.sql import select

from nwc_backend.db import db
from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.get_budget_handler import get_budget
from nwc_backend.exceptions import Nip47RequestException
from nwc_backend.models.__tests__.model_examples import (
    create_nip47_request,
    create_nip47_request_with_spending_limit,
)
from nwc_backend.models.spending_cycle import SpendingCycle


@patch.object(aiohttp.ClientSession, "post")
async def test_get_budget__spending_limit_disabled(
    mock_post: Mock, test_client: QuartClient
) -> None:
    mock_response = AsyncMock()
    mock_post.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        request = await create_nip47_request(params={})
        response = await get_budget(access_token=token_hex(), request=request)

        mock_post.assert_not_called()
        assert exclude_none_values(response.to_dict()) == {}


@patch.object(aiohttp.ClientSession, "get")
async def test_get_budget_failure__http_raises(
    mock_get: Mock, test_client: QuartClient
) -> None:
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.ok = False
    mock_get.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        request = await create_nip47_request_with_spending_limit("USD", 1000, params={})
        with pytest.raises(Nip47RequestException) as exc_info:
            await get_budget(access_token=token_hex(), request=request)
            assert exc_info.value.error_code == ErrorCode.INTERNAL


@patch.object(aiohttp.ClientSession, "get")
async def test_get_budget_success__spending_limit_SAT_enabled(
    mock_get_budget_estimate: Mock, test_client: QuartClient
) -> None:
    async with test_client.app.app_context():
        request = await create_nip47_request_with_spending_limit("SAT", 1000, params={})
        response = await get_budget(access_token=token_hex(), request=request)

        mock_get_budget_estimate.assert_not_called()
        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        assert exclude_none_values(response.to_dict()) == {
            "total_budget_msats": 1000000,
            "remaining_budget_msats": 1000000,
            "renews_at": round(spending_cycle.end_time.timestamp()),
        }


@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_success__spending_limit_USD_enabled(
    mock_get_budget_estimate: Mock, test_client: QuartClient
) -> None:
    fake_multiplier = 50
    total_budget_currency_amount = 1000
    estimated_budget_currency_amount = total_budget_currency_amount * fake_multiplier
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(
        return_value=json.dumps(
            {
                "estimated_budget_currency_amount": estimated_budget_currency_amount,
            }
        )
    )
    mock_response.ok = True
    mock_get_budget_estimate.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        request = await create_nip47_request_with_spending_limit(
            "USD", total_budget_currency_amount, params={}
        )
        response = await get_budget(access_token=token_hex(), request=request)

        mock_get_budget_estimate.assert_called_once_with(
            url="/budget_estimate",
            params={
                "sending_currency_code": "USD",
                "sending_currency_amount": total_budget_currency_amount,
                "budget_currency_code": "SAT",
            },
            headers=ANY,
        )
        assert exclude_none_values(response.to_dict()) == {
            "total_budget_msats": estimated_budget_currency_amount * 1000,
            "remaining_budget_msats": estimated_budget_currency_amount * 1000,
            "renews_at": ANY,
            "currency": {
                "code": "USD",
                "total_budget": total_budget_currency_amount,
                "remaining_budget": total_budget_currency_amount,
                "symbol": "$",
                "name": "US Dollar",
                "decimals": 2,
            },
        }
