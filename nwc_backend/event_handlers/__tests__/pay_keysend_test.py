# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import math
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from pydantic_core import ValidationError
from quart.app import QuartClient
from sqlalchemy.sql import select
from uma_auth.models.error_response import ErrorCode as VaspErrorCode
from uma_auth.models.error_response import ErrorResponse as VaspErrorResponse
from uma_auth.models.pay_keysend_request import PayKeysendRequest

from nwc_backend.db import db
from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.pay_keysend_handler import pay_keysend
from nwc_backend.exceptions import InsufficientBudgetException, Nip47RequestException
from nwc_backend.models.__tests__.model_examples import (
    create_nip47_request,
    create_nip47_with_spending_limit,
)
from nwc_backend.models.nip47_request import ErrorCode
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_cycle_payment import (
    PaymentStatus,
    SpendingCyclePayment,
)
from nwc_backend.typing import none_throws


@patch.object(aiohttp.ClientSession, "post")
async def test_pay_keysend_success(mock_post: Mock, test_client: QuartClient) -> None:
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_post.return_value.__aenter__.return_value = mock_response

    params = {
        "pubkey": token_hex(),
        "amount": 10000,
        "tlv_records": [{"type": 5482373484, "value": "0123456789abcdef"}],
    }
    async with test_client.app.app_context():
        request = await create_nip47_request(params=params)
        response = await pay_keysend(access_token=token_hex(), request=request)

        mock_post.assert_called_once_with(
            url="/payments/keysend",
            data=PayKeysendRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        assert exclude_none_values(response.to_dict()) == vasp_response


async def test_pay_keysend_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(ValidationError):
            request = await create_nip47_request(
                params={"pubkey": token_hex(), "amount": "abc"}
            )
            await pay_keysend(access_token=token_hex(), request=request)


@patch.object(aiohttp.ClientSession, "post")
async def test_pay_keysend_failure__http_raises(
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
            request = await create_nip47_request(
                params={"pubkey": token_hex(), "amount": 10000}
            )
            await pay_keysend(access_token=token_hex(), request=request)
        assert exc_info.value.error_code == ErrorCode.PAYMENT_FAILED
        assert exc_info.value.error_message == vasp_response.message


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_keysend_success__spending_limit_SAT_enabled(
    mock_get_budget_estimate: Mock, mock_pay_keysend: Mock, test_client: QuartClient
) -> None:
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_keysend.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        payment_amount_msats = 1023
        payment_amount_sats = 2
        params = {"pubkey": token_hex(), "amount": payment_amount_msats}
        request = await create_nip47_with_spending_limit("SAT", 1000, params)
        response = await pay_keysend(access_token=token_hex(), request=request)

        mock_pay_keysend.assert_called_once_with(
            url="/payments/keysend",
            data=PayKeysendRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()
        assert exclude_none_values(response.to_dict()) == vasp_response

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(
            request.app_connection.nwc_connection.spending_limit
        )
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency_code
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == payment_amount_sats
        assert spending_cycle.total_spent_on_hold == 0

        spending_payment = (
            await db.session.execute(select(SpendingCyclePayment))
        ).scalar_one()
        assert spending_payment.spending_cycle_id == spending_cycle.id
        assert spending_payment.estimated_amount == payment_amount_sats
        assert spending_payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"] * payment_amount_sats
        )
        assert spending_payment.settled_amount == payment_amount_sats
        assert spending_payment.status == PaymentStatus.SUCCEEDED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_keysend_payment_failed__spending_limit_SAT_enabled(
    mock_get_budget_estimate: Mock, mock_pay_keysend: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {
            "code": VaspErrorCode.PAYMENT_FAILED.name,
            "message": "No route.",
        }
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_pay_keysend.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        payment_amount_msats = 5000
        payment_amount_sats = 5
        params = {"pubkey": token_hex(), "amount": payment_amount_msats}
        request = await create_nip47_with_spending_limit("SAT", 1000, params)

        with pytest.raises(Nip47RequestException):
            await pay_keysend(access_token=token_hex(), request=request)
            mock_pay_keysend.assert_called_once_with(
                url="/payments/keysend",
                data=PayKeysendRequest.from_dict(params).to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(
            request.app_connection.nwc_connection.spending_limit
        )
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency_code
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0

        spending_payment = (
            await db.session.execute(select(SpendingCyclePayment))
        ).scalar_one()
        assert spending_payment.spending_cycle_id == spending_cycle.id
        assert spending_payment.estimated_amount == payment_amount_sats
        assert spending_payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"] * payment_amount_sats
        )
        assert spending_payment.settled_amount is None
        assert spending_payment.status == PaymentStatus.FAILED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_budget_not_enough__spending_limit_SAT_enabled(
    mock_get_budget_estimate: Mock, mock_pay_keysend: Mock, test_client: QuartClient
) -> None:
    async with test_client.app.app_context():
        payment_amount_msats = 1200_000
        params = {"pubkey": token_hex(), "amount": payment_amount_msats}
        request = await create_nip47_with_spending_limit("SAT", 1000, params)

        with pytest.raises(InsufficientBudgetException):
            await pay_keysend(access_token=token_hex(), request=request)
            mock_pay_keysend.assert_not_called()
            mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(
            request.app_connection.nwc_connection.spending_limit
        )
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency_code
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_keysend_success__spending_limit_USD_enabled(
    mock_get_budget_estimate: Mock, mock_pay_keysend: Mock, test_client: QuartClient
) -> None:
    final_budget_currency_amount = 111
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "total_budget_currency_amount": final_budget_currency_amount,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_keysend.return_value.__aenter__.return_value = mock_response

    estimated_budget_currency_amount = 112
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
        payment_amount_msats = 1000_000
        payment_amount_sats = 1000
        params = {"pubkey": token_hex(), "amount": payment_amount_msats}
        request = await create_nip47_with_spending_limit("USD", 10000, params)
        response = await pay_keysend(access_token=token_hex(), request=request)

        params["budget_currency_code"] = "USD"
        mock_pay_keysend.assert_called_once_with(
            url="/payments/keysend",
            data=PayKeysendRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_called_once_with(
            url="/budget_estimate",
            params={
                "sending_currency_code": "SAT",
                "sending_currency_amount": payment_amount_sats,
                "budget_currency_code": "USD",
            },
            headers=ANY,
        )
        assert exclude_none_values(response.to_dict()) == vasp_response

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(
            request.app_connection.nwc_connection.spending_limit
        )
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency_code
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == final_budget_currency_amount
        assert spending_cycle.total_spent_on_hold == 0

        spending_payment = (
            await db.session.execute(select(SpendingCyclePayment))
        ).scalar_one()
        assert spending_payment.spending_cycle_id == spending_cycle.id
        assert spending_payment.estimated_amount == estimated_budget_currency_amount
        assert spending_payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"]
            * estimated_budget_currency_amount
        )
        assert spending_payment.settled_amount == final_budget_currency_amount
        assert spending_payment.status == PaymentStatus.SUCCEEDED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_keysend_payment_failed__spending_limit_USD_enabled(
    mock_get_budget_estimate: Mock, mock_pay_keysend: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {
            "code": VaspErrorCode.PAYMENT_FAILED.name,
            "message": "No route.",
        }
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_pay_keysend.return_value.__aenter__.return_value = mock_response

    estimated_budget_currency_amount = 112
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
        payment_amount_msats = 1000_000
        payment_amount_sats = 1000
        params = {"pubkey": token_hex(), "amount": payment_amount_msats}
        request = await create_nip47_with_spending_limit("USD", 10000, params)

        with pytest.raises(Nip47RequestException):
            await pay_keysend(access_token=token_hex(), request=request)

            mock_pay_keysend.assert_called_once_with(
                url="/payments/keysend",
                data=PayKeysendRequest.from_dict(params).to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_called_once_with(
                url="/budget_estimate",
                params={
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": payment_amount_sats,
                    "budget_currency_code": "USD",
                },
                headers=ANY,
            )

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(
            request.app_connection.nwc_connection.spending_limit
        )
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency_code
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0

        spending_payment = (
            await db.session.execute(select(SpendingCyclePayment))
        ).scalar_one()
        assert spending_payment.spending_cycle_id == spending_cycle.id
        assert spending_payment.estimated_amount == estimated_budget_currency_amount
        assert spending_payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"]
            * estimated_budget_currency_amount
        )
        assert spending_payment.settled_amount is None
        assert spending_payment.status == PaymentStatus.FAILED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_budget_not_enough__spending_limit_USD_enabled(
    mock_get_budget_estimate: Mock, mock_pay_keysend: Mock, test_client: QuartClient
) -> None:
    estimated_budget_currency_amount = 112
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
        payment_amount_msats = 1000_000
        payment_amount_sats = 1000
        params = {"pubkey": token_hex(), "amount": payment_amount_msats}
        request = await create_nip47_with_spending_limit("USD", 100, params)

        with pytest.raises(InsufficientBudgetException):
            await pay_keysend(access_token=token_hex(), request=request)
            mock_pay_keysend.assert_not_called()
            mock_get_budget_estimate.assert_called_once_with(
                url="/budget_estimate",
                params={
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": payment_amount_sats,
                    "budget_currency_code": "USD",
                },
                headers=ANY,
            )

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(
            request.app_connection.nwc_connection.spending_limit
        )
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency_code
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0
