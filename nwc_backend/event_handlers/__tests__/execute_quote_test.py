# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import math
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from quart.app import QuartClient
from sqlalchemy.sql import select
from uma_auth.models.error_response import ErrorCode as VaspErrorCode
from uma_auth.models.error_response import ErrorResponse as VaspErrorResponse
from uma_auth.models.execute_quote_request import ExecuteQuoteRequest

from nwc_backend.db import db
from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.execute_quote_handler import execute_quote
from nwc_backend.exceptions import (
    InsufficientBudgetException,
    InvalidInputException,
    Nip47RequestException,
)
from nwc_backend.models.__tests__.model_examples import (
    create_nip47_request,
    create_nip47_request_with_spending_limit,
    create_payment_quote,
)
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.outgoing_payment import (
    OutgoingPayment,
    PaymentStatus,
    ReceivingAddressType,
)
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.typing import none_throws


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_execute_quote_success__spending_limit_disabled__sending_SAT_budget_SAT(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
) -> None:
    vasp_response = {"preimage": token_hex()}
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_execute_quote.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        quote = await create_payment_quote(sending_currency_code="SAT")
        request = await create_nip47_request(
            params={"payment_hash": quote.payment_hash}, budget_currency_code="SAT"
        )
        response = await execute_quote(access_token=token_hex(), request=request)
        assert exclude_none_values(response.to_dict()) == vasp_response

        mock_execute_quote.assert_called_once_with(
            url=f"/quote/{quote.payment_hash}",
            data=ExecuteQuoteRequest(budget_currency_code=None).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == quote.receiver_address
        assert payment.sending_currency_code == quote.sending_currency_code
        assert payment.sending_currency_amount == quote.sending_currency_amount
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount == quote.sending_currency_amount
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.quote_id == quote.id


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_execute_quote_success__spending_limit_disabled__sending_SAT_budget_USD(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
) -> None:
    total_budget_currency_amount = 100
    vasp_response = {
        "preimage": token_hex(),
        "total_budget_currency_amount": total_budget_currency_amount,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_execute_quote.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        quote = await create_payment_quote(sending_currency_code="SAT")
        request = await create_nip47_request(
            params={"payment_hash": quote.payment_hash}, budget_currency_code="USD"
        )
        response = await execute_quote(access_token=token_hex(), request=request)
        assert exclude_none_values(response.to_dict()) == vasp_response

        mock_execute_quote.assert_called_once_with(
            url=f"/quote/{quote.payment_hash}",
            data=ExecuteQuoteRequest(budget_currency_code="USD").to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == quote.receiver_address
        assert payment.sending_currency_code == quote.sending_currency_code
        assert payment.sending_currency_amount == quote.sending_currency_amount
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount == total_budget_currency_amount
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.quote_id == quote.id


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_execute_quote_payment_failed__spending_limit_disabled(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
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
    mock_execute_quote.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        quote = await create_payment_quote()
        request = await create_nip47_request(
            params={"payment_hash": quote.payment_hash}
        )

        with pytest.raises(Nip47RequestException):
            await execute_quote(access_token=token_hex(), request=request)
            mock_execute_quote.assert_called_once_with(
                url=f"/quote/{quote.payment_hash}",
                data=ExecuteQuoteRequest(budget_currency_code=None).to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_not_called()

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == quote.receiver_address
        assert payment.sending_currency_code == quote.sending_currency_code
        assert payment.sending_currency_amount == quote.sending_currency_amount
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.FAILED
        assert payment.quote_id == quote.id


async def test_execute_quote_failure__invalid_input(test_client: QuartClient) -> None:
    with pytest.raises(InvalidInputException):
        async with test_client.app.app_context():
            await execute_quote(
                access_token=token_hex(),
                request=Nip47Request(params={"payment_hashh": token_hex()}),
            )


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_execute_quote_success__sending_SAT_budget_SAT(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
) -> None:
    vasp_response = {"preimage": token_hex()}
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_execute_quote.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        quote = await create_payment_quote(
            sending_currency_amount=100_000, sending_currency_code="SAT"
        )
        request = await create_nip47_request_with_spending_limit(
            spending_limit_currency_code="SAT",
            spending_limit_currency_amount=200_000,
            params={"payment_hash": quote.payment_hash},
        )
        response = await execute_quote(access_token=token_hex(), request=request)
        assert exclude_none_values(response.to_dict()) == vasp_response

        mock_execute_quote.assert_called_once_with(
            url=f"/quote/{quote.payment_hash}",
            data=ExecuteQuoteRequest(budget_currency_code=None).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == quote.sending_currency_amount
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == quote.receiver_address
        assert payment.sending_currency_code == quote.sending_currency_code
        assert payment.sending_currency_amount == quote.sending_currency_amount
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.estimated_budget_currency_amount == quote.sending_currency_amount
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"]
            * quote.sending_currency_amount
        )
        assert payment.settled_budget_currency_amount == quote.sending_currency_amount
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.quote_id == quote.id


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_execute_quote_payment_failed__sending_SAT_budget_SAT(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
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
    mock_execute_quote.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        quote = await create_payment_quote(
            sending_currency_amount=100_000, sending_currency_code="SAT"
        )
        request = await create_nip47_request_with_spending_limit(
            spending_limit_currency_code="SAT",
            spending_limit_currency_amount=200_000,
            params={"payment_hash": quote.payment_hash},
        )

        with pytest.raises(Nip47RequestException):
            await execute_quote(access_token=token_hex(), request=request)

            mock_execute_quote.assert_called_once_with(
                url=f"/quote/{quote.payment_hash}",
                data=ExecuteQuoteRequest(budget_currency_code=None).to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == quote.receiver_address
        assert payment.sending_currency_code == quote.sending_currency_code
        assert payment.sending_currency_amount == quote.sending_currency_amount
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.estimated_budget_currency_amount == quote.sending_currency_amount
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"]
            * quote.sending_currency_amount
        )
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.FAILED
        assert payment.quote_id == quote.id


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_budget_not_enough__sending_SAT_budget_SAT(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
) -> None:
    async with test_client.app.app_context():
        quote = await create_payment_quote(
            sending_currency_amount=1000_000, sending_currency_code="SAT"
        )
        request = await create_nip47_request_with_spending_limit(
            spending_limit_currency_code="SAT",
            spending_limit_currency_amount=200_000,
            params={"payment_hash": quote.payment_hash},
        )

        with pytest.raises(InsufficientBudgetException):
            await execute_quote(access_token=token_hex(), request=request)
            mock_execute_quote.assert_not_called()
            mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_execute_quote_success__sending_SAT_budget_USD(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
) -> None:
    final_budget_currency_amount = 111
    vasp_response = {
        "preimage": token_hex(),
        "total_budget_currency_amount": final_budget_currency_amount,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_execute_quote.return_value.__aenter__.return_value = mock_response

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
        quote = await create_payment_quote(
            sending_currency_amount=100_000, sending_currency_code="SAT"
        )
        request = await create_nip47_request_with_spending_limit(
            spending_limit_currency_code="USD",
            spending_limit_currency_amount=200,
            params={"payment_hash": quote.payment_hash},
        )
        response = await execute_quote(access_token=token_hex(), request=request)
        assert exclude_none_values(response.to_dict()) == vasp_response

        mock_execute_quote.assert_called_once_with(
            url=f"/quote/{quote.payment_hash}",
            data=ExecuteQuoteRequest(budget_currency_code="USD").to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_called_once_with(
            url="/budget_estimate",
            params={
                "sending_currency_code": quote.sending_currency_code,
                "sending_currency_amount": quote.sending_currency_amount,
                "budget_currency_code": "USD",
            },
            headers=ANY,
        )

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == final_budget_currency_amount
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == quote.receiver_address
        assert payment.sending_currency_code == quote.sending_currency_code
        assert payment.sending_currency_amount == quote.sending_currency_amount
        assert payment.spending_cycle_id == spending_cycle.id
        assert (
            payment.estimated_budget_currency_amount == estimated_budget_currency_amount
        )
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"]
            * estimated_budget_currency_amount
        )
        assert payment.settled_budget_currency_amount == final_budget_currency_amount
        assert payment.status == PaymentStatus.SUCCEEDED
        assert payment.quote_id == quote.id


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_execute_quote_payment_failed__sending_SAT_budget_USD(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
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
    mock_execute_quote.return_value.__aenter__.return_value = mock_response

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
        quote = await create_payment_quote(
            sending_currency_amount=100_000, sending_currency_code="SAT"
        )
        request = await create_nip47_request_with_spending_limit(
            spending_limit_currency_code="USD",
            spending_limit_currency_amount=200,
            params={"payment_hash": quote.payment_hash},
        )

        with pytest.raises(Nip47RequestException):
            await execute_quote(access_token=token_hex(), request=request)

            mock_execute_quote.assert_called_once_with(
                url=f"/quote/{quote.payment_hash}",
                data=ExecuteQuoteRequest(budget_currency_code="USD").to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_called_once_with(
                url="/budget_estimate",
                params={
                    "sending_currency_code": quote.sending_currency_code,
                    "sending_currency_amount": quote.sending_currency_amount,
                    "budget_currency_code": "USD",
                },
                headers=ANY,
            )

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == quote.receiver_address
        assert payment.sending_currency_code == quote.sending_currency_code
        assert payment.sending_currency_amount == quote.sending_currency_amount
        assert payment.spending_cycle_id == spending_cycle.id
        assert (
            payment.estimated_budget_currency_amount == estimated_budget_currency_amount
        )
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"]
            * estimated_budget_currency_amount
        )
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.FAILED
        assert payment.quote_id == quote.id


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_budget_not_enough__sending_SAT_budget_USD(
    mock_get_budget_estimate: Mock, mock_execute_quote: Mock, test_client: QuartClient
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
        quote = await create_payment_quote(
            sending_currency_amount=100_000, sending_currency_code="SAT"
        )
        request = await create_nip47_request_with_spending_limit(
            spending_limit_currency_code="USD",
            spending_limit_currency_amount=100,
            params={"payment_hash": quote.payment_hash},
        )

        with pytest.raises(InsufficientBudgetException):
            await execute_quote(access_token=token_hex(), request=request)

            mock_execute_quote.assert_not_called()
            mock_get_budget_estimate.assert_called_once_with(
                url="/budget_estimate",
                params={
                    "sending_currency_code": quote.sending_currency_code,
                    "sending_currency_amount": quote.sending_currency_amount,
                    "budget_currency_code": "USD",
                },
                headers=ANY,
            )

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0


async def test_execute_quote_failed__unrecognized_payment_hash(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        request = await create_nip47_request(params={"payment_hash": token_hex()})

        with pytest.raises(InvalidInputException):
            await execute_quote(access_token=token_hex(), request=request)
