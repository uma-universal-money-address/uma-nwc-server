# pyre-strict

import json
import math
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from nostr_sdk import ErrorCode
from pydantic_core import ValidationError
from quart.app import QuartClient
from sqlalchemy.sql import select
from uma_auth.models.error_response import ErrorCode as VaspErrorCode
from uma_auth.models.error_response import ErrorResponse as VaspErrorResponse
from uma_auth.models.pay_invoice_request import PayInvoiceRequest

from nwc_backend.db import db
from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.pay_invoice_handler import pay_invoice
from nwc_backend.exceptions import InsufficientBudgetException, Nip47RequestException
from nwc_backend.models.__tests__.model_examples import (
    create_nip47_request,
    create_nip47_request_with_spending_limit,
)
from nwc_backend.models.outgoing_payment import (
    OutgoingPayment,
    PaymentStatus,
    ReceivingAddressType,
)
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.typing import none_throws

INVOICE = "lnbc1pj794v0pp53yddnj782m5ydlya6t3rv9vmys9jmh8neyp6nrr282su9ygpw0vqdqj8f3k7mmvvdhhyete8gcqzpgxqyz5vqrzjqtqd37k2ya0pv8pqeyjs4lklcexjyw600g9qqp62r4j0ph8fcmlfwqqqqrwkcy8e25qqqqqqqqqqqqqq9qsp5xct2ycymvacgnpjdstsfhkw9anm6t94hfftlrzththjsvnnu6d8s9qyyssqgpuzv6x8kfaua437jh7xll78ckk23hqzjlz8lgtc7lp7dpwn394k5eyuz30687esccct8cgjd46cl6enlzkhza0rlsmfsdxx32t957sqsfujf3"


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_success__spending_limit_disabled__budget_SAT(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_invoice.return_value.__aenter__.return_value = mock_response

    payment_amount_msats = 1030
    payment_amount_sats = 2
    params = {"invoice": INVOICE, "amount": payment_amount_msats}
    async with test_client.app.app_context():
        request = await create_nip47_request(params=params, budget_currency_code="SAT")
        response = await pay_invoice(access_token=token_hex(), request=request)

        mock_pay_invoice.assert_called_once_with(
            url="/payments/bolt11",
            data=PayInvoiceRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()
        assert exclude_none_values(response.to_dict()) == vasp_response

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.BOLT11
        assert payment.receiver == INVOICE
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == payment_amount_sats
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount == payment_amount_sats
        assert payment.status == PaymentStatus.SUCCEEDED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_success__spending_limit_disabled__budget_USD(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    total_budget_currency_amount = 100
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "total_budget_currency_amount": total_budget_currency_amount,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_invoice.return_value.__aenter__.return_value = mock_response

    payment_amount_msats = 1030
    payment_amount_sats = 2
    params = {"invoice": INVOICE, "amount": payment_amount_msats}
    async with test_client.app.app_context():
        request = await create_nip47_request(params=params, budget_currency_code="USD")
        response = await pay_invoice(access_token=token_hex(), request=request)

        params["budget_currency_code"] = "USD"
        mock_pay_invoice.assert_called_once_with(
            url="/payments/bolt11",
            data=PayInvoiceRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()
        assert exclude_none_values(response.to_dict()) == vasp_response

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.BOLT11
        assert payment.receiver == INVOICE
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == payment_amount_sats
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount == total_budget_currency_amount
        assert payment.status == PaymentStatus.SUCCEEDED


async def test_pay_invoice_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        request = await create_nip47_request(params={"payment_hashh": token_hex()})
        with pytest.raises(ValidationError):
            await pay_invoice(access_token=token_hex(), request=request)


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_payment_failed__spending_limit_disabled(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {
            "code": VaspErrorCode.PAYMENT_FAILED.name,
            "message": "Invoice has already been paid.",
        }
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_pay_invoice.return_value.__aenter__.return_value = mock_response

    payment_amount_msats = 1030
    payment_amount_sats = 2
    async with test_client.app.app_context():
        params = {"invoice": INVOICE, "amount": payment_amount_msats}
        request = await create_nip47_request(params=params)
        with pytest.raises(Nip47RequestException) as exc_info:
            await pay_invoice(access_token=token_hex(), request=request)
            assert exc_info.value.error_code == ErrorCode.PAYMENT_FAILED
            assert exc_info.value.error_message == vasp_response.message

            mock_pay_invoice.assert_called_once_with(
                url="/payments/bolt11",
                data=PayInvoiceRequest.from_dict(params).to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_not_called()

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.BOLT11
        assert payment.receiver == INVOICE
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == payment_amount_sats
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.FAILED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_success__spending_limit_SAT_enabled(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_invoice.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        payment_amount_msats = 1030
        payment_amount_sats = 2
        params = {"invoice": INVOICE, "amount": payment_amount_msats}
        request = await create_nip47_request_with_spending_limit("SAT", 1000, params)
        response = await pay_invoice(access_token=token_hex(), request=request)

        mock_pay_invoice.assert_called_once_with(
            url="/payments/bolt11",
            data=PayInvoiceRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()
        assert exclude_none_values(response.to_dict()) == vasp_response

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == payment_amount_sats
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.BOLT11
        assert payment.receiver == INVOICE
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == payment_amount_sats
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.estimated_budget_currency_amount == payment_amount_sats
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"] * payment_amount_sats
        )
        assert payment.settled_budget_currency_amount == payment_amount_sats
        assert payment.status == PaymentStatus.SUCCEEDED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_payment_failed__spending_limit_SAT_enabled(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {
            "code": VaspErrorCode.PAYMENT_FAILED.name,
            "message": "Invoice has already been paid.",
        }
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_pay_invoice.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        payment_amount_msats = 1000
        payment_amount_sats = 1
        params = {"invoice": INVOICE, "amount": payment_amount_msats}
        request = await create_nip47_request_with_spending_limit("SAT", 1000, params)

        with pytest.raises(Nip47RequestException):
            await pay_invoice(access_token=token_hex(), request=request)
            mock_pay_invoice.assert_called_once_with(
                url="/payments/bolt11",
                data=PayInvoiceRequest.from_dict(params).to_json(),
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
        assert payment.receiver_type == ReceivingAddressType.BOLT11
        assert payment.receiver == INVOICE
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == payment_amount_sats
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.estimated_budget_currency_amount == payment_amount_sats
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"] * payment_amount_sats
        )
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.FAILED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_budget_not_enough__spending_limit_SAT_enabled(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    async with test_client.app.app_context():
        payment_amount_msats = 1200_000
        params = {"invoice": INVOICE, "amount": payment_amount_msats}
        request = await create_nip47_request_with_spending_limit("SAT", 1000, params)

        with pytest.raises(InsufficientBudgetException):
            await pay_invoice(access_token=token_hex(), request=request)
            mock_pay_invoice.assert_not_called()
            mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_success__spending_limit_USD_enabled(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    final_budget_currency_amount = 111
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "total_budget_currency_amount": final_budget_currency_amount,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_invoice.return_value.__aenter__.return_value = mock_response

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
        params = {"invoice": INVOICE, "amount": payment_amount_msats}
        request = await create_nip47_request_with_spending_limit("USD", 10000, params)
        response = await pay_invoice(access_token=token_hex(), request=request)

        params["budget_currency_code"] = "USD"
        mock_pay_invoice.assert_called_once_with(
            url="/payments/bolt11",
            data=PayInvoiceRequest.from_dict(params).to_json(),
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
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == final_budget_currency_amount
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.BOLT11
        assert payment.receiver == INVOICE
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == payment_amount_sats
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


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_invoice_payment_failed__spending_limit_USD_enabled(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {
            "code": VaspErrorCode.PAYMENT_FAILED.name,
            "message": "Invoice has already been paid.",
        }
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_pay_invoice.return_value.__aenter__.return_value = mock_response

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
        params = {"invoice": INVOICE, "amount": payment_amount_msats}
        request = await create_nip47_request_with_spending_limit("USD", 1000, params)

        with pytest.raises(Nip47RequestException):
            await pay_invoice(access_token=token_hex(), request=request)

            mock_pay_invoice.assert_called_once_with(
                url="/payments/bolt11",
                data=PayInvoiceRequest.from_dict(params).to_json(),
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
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.BOLT11
        assert payment.receiver == INVOICE
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == payment_amount_sats
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


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_budget_not_enough__spending_limit_USD_enabled(
    mock_get_budget_estimate: Mock, mock_pay_invoice: Mock, test_client: QuartClient
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
        params = {"invoice": INVOICE, "amount": payment_amount_msats}
        request = await create_nip47_request_with_spending_limit("USD", 100, params)

        with pytest.raises(InsufficientBudgetException):
            await pay_invoice(access_token=token_hex(), request=request)
            mock_pay_invoice.assert_not_called()
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
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0
