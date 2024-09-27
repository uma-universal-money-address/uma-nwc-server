# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import math
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from unittest.mock import ANY, AsyncMock, Mock, patch

import aiohttp
import pytest
from pydantic_core import ValidationError
from quart.app import QuartClient
from sqlalchemy.sql import select
from uma_auth.models.error_response import ErrorCode as VaspErrorCode
from uma_auth.models.error_response import ErrorResponse as VaspErrorResponse
from uma_auth.models.pay_to_address_request import PayToAddressRequest

from nwc_backend.db import db
from nwc_backend.event_handlers.__tests__.utils import exclude_none_values
from nwc_backend.event_handlers.pay_to_address_handler import pay_to_address
from nwc_backend.exceptions import (
    InsufficientBudgetException,
    InvalidInputException,
    Nip47RequestException,
)
from nwc_backend.models.__tests__.model_examples import (
    create_currency,
    create_nip47_request,
    create_nip47_request_with_spending_limit,
)
from nwc_backend.models.nip47_request import ErrorCode
from nwc_backend.models.outgoing_payment import (
    OutgoingPayment,
    PaymentStatus,
    ReceivingAddressType,
)
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.typing import none_throws


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_to_address_success__spending_limit_disabled(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
) -> None:
    now = datetime.now(timezone.utc)
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "quote": {
            "sending_currency": create_currency("SAT").to_dict(),
            "receiving_currency": create_currency("USD").to_dict(),
            "payment_hash": token_hex(),
            "expires_at": int((now + timedelta(minutes=5)).timestamp()),
            "multiplier": 15351.4798,
            "fees": 10,
            "total_sending_amount": 1_000_000,
            "total_receiving_amount": 65,
            "created_at": int(now.timestamp()),
        },
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_to_address.return_value.__aenter__.return_value = mock_response

    sending_currency_amount = 1_000_000
    receiver_address = "$alice@uma.me"
    params = {
        "receiver": {"lud16": receiver_address},
        "sending_currency_code": "SAT",
        "sending_currency_amount": sending_currency_amount,
    }
    async with test_client.app.app_context():
        request = await create_nip47_request(params=params)
        response = await pay_to_address(access_token=token_hex(), request=request)

        params["receiver_address"] = params.pop("receiver")["lud16"]  # pyre-ignore[16]
        mock_pay_to_address.assert_called_once_with(
            url="/payments/lud16",
            data=PayToAddressRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()
        assert exclude_none_values(response.to_dict()) == vasp_response

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == receiver_address
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == sending_currency_amount
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.SUCCEEDED


async def test_pay_to_address_failure__no_receiver(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            request = await create_nip47_request(
                params={
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": 1_000_000,
                }
            )
            await pay_to_address(access_token=token_hex(), request=request)


async def test_pay_to_address_failure__multiple_receivers(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        with pytest.raises(InvalidInputException):
            request = await create_nip47_request(
                params={
                    "receiver": {
                        "lud16": "$alice@uma.me",
                        "bolt12": "lno1qqszqfnjxapqxqrrzd9hxyarjwpzqarhdaexgmm9wejkgtm9venj2cmyde3x7urpwp8xgetr5fpqqg5w",
                    },
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": 1_000_000,
                }
            )
            await pay_to_address(access_token=token_hex(), request=request)


async def test_pay_to_address_failure__invalid_input(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        with pytest.raises(ValidationError):
            request = await create_nip47_request(
                params={
                    "receiver": {"lud16": "$alice@uma.me"},
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": "amount",  # should be integer
                }
            )
            await pay_to_address(access_token=token_hex(), request=request)


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_to_address_payment_failed__spending_limit_disabled(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
) -> None:
    vasp_response = VaspErrorResponse.from_dict(
        {"code": VaspErrorCode.PAYMENT_FAILED.name, "message": "No route."}
    )
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=vasp_response.model_dump_json())
    mock_response.ok = False
    mock_pay_to_address.return_value.__aenter__.return_value = mock_response

    sending_currency_amount = 1_000_000
    receiver_address = "$alice@uma.me"
    async with test_client.app.app_context():
        with pytest.raises(Nip47RequestException) as exc_info:
            request = await create_nip47_request(
                params={
                    "receiver": {"lud16": receiver_address},
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": sending_currency_amount,
                }
            )
            await pay_to_address(access_token=token_hex(), request=request)
            assert exc_info.value.error_code == ErrorCode.PAYMENT_FAILED
            assert exc_info.value.error_message == vasp_response.message
            mock_get_budget_estimate.assert_not_called()

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == receiver_address
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == sending_currency_amount
        assert payment.spending_cycle_id is None
        assert payment.estimated_budget_currency_amount is None
        assert payment.budget_on_hold is None
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.FAILED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_to_address_success__sending_SAT_budget_SAT(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
) -> None:
    now = datetime.now(timezone.utc)
    total_sending_amount = 1000
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "quote": {
            "sending_currency": create_currency("SAT").to_dict(),
            "receiving_currency": create_currency("USD").to_dict(),
            "payment_hash": token_hex(),
            "expires_at": int((now + timedelta(minutes=5)).timestamp()),
            "multiplier": 15351.4798,
            "fees": 10,
            "total_sending_amount": total_sending_amount,
            "total_receiving_amount": 65,
            "created_at": int(now.timestamp()),
        },
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_to_address.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        receiver_address = "$alice@uma.me"
        params = {
            "receiver": {"lud16": receiver_address},
            "sending_currency_code": "SAT",
            "sending_currency_amount": total_sending_amount,
        }
        request = await create_nip47_request_with_spending_limit("SAT", 5000, params)
        response = await pay_to_address(access_token=token_hex(), request=request)

        params["receiver_address"] = params.pop("receiver")["lud16"]  # pyre-ignore[16]
        mock_pay_to_address.assert_called_once_with(
            url="/payments/lud16",
            data=PayToAddressRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_not_called()
        assert exclude_none_values(response.to_dict()) == vasp_response

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == total_sending_amount
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == receiver_address
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == total_sending_amount
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.estimated_budget_currency_amount == total_sending_amount
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"] * total_sending_amount
        )
        assert payment.settled_budget_currency_amount == total_sending_amount
        assert payment.status == PaymentStatus.SUCCEEDED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_to_address_payment_failed__sending_SAT_budget_SAT(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
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
    mock_pay_to_address.return_value.__aenter__.return_value = mock_response

    async with test_client.app.app_context():
        total_sending_amount = 1000
        receiver_address = "$alice@uma.me"
        params = {
            "receiver": {"lud16": receiver_address},
            "sending_currency_code": "SAT",
            "sending_currency_amount": total_sending_amount,
        }
        request = await create_nip47_request_with_spending_limit("SAT", 5000, params)

        with pytest.raises(Nip47RequestException):
            await pay_to_address(access_token=token_hex(), request=request)

            params["receiver_address"] = params.pop("receiver")[  # pyre-ignore[16]
                "lud16"
            ]
            mock_pay_to_address.assert_called_once_with(
                url="/payments/lud16",
                data=PayToAddressRequest.from_dict(params).to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == receiver_address
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == total_sending_amount
        assert payment.spending_cycle_id == spending_cycle.id
        assert payment.estimated_budget_currency_amount == total_sending_amount
        assert payment.budget_on_hold == math.ceil(
            test_client.app.config["BUDGET_BUFFER_MULTIPLIER"] * total_sending_amount
        )
        assert payment.settled_budget_currency_amount is None
        assert payment.status == PaymentStatus.FAILED


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_budget_not_enough__sending_SAT_budget_SAT(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
) -> None:
    async with test_client.app.app_context():
        total_sending_amount = 6000
        params = {
            "receiver": {"lud16": "$alice@uma.me"},
            "sending_currency_code": "SAT",
            "sending_currency_amount": total_sending_amount,
        }
        request = await create_nip47_request_with_spending_limit("SAT", 5000, params)

        with pytest.raises(InsufficientBudgetException):
            await pay_to_address(access_token=token_hex(), request=request)
            mock_pay_to_address.assert_not_called()
            mock_get_budget_estimate.assert_not_called()

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0


@patch.object(aiohttp.ClientSession, "post")
@patch.object(aiohttp.ClientSession, "get")
async def test_pay_to_address_success__sending_SAT_budget_USD(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
) -> None:
    final_budget_currency_amount = 111
    now = datetime.now(timezone.utc)
    total_sending_amount = 1000
    vasp_response = {
        "preimage": "b6f1086f61561bacf2f05fa02ab30a06c3432c1aea62817c019ea33c1730eeb3",
        "quote": {
            "sending_currency": create_currency("SAT").to_dict(),
            "receiving_currency": create_currency("USD").to_dict(),
            "payment_hash": token_hex(),
            "expires_at": int((now + timedelta(minutes=5)).timestamp()),
            "multiplier": 15351.4798,
            "fees": 10,
            "total_sending_amount": total_sending_amount,
            "total_receiving_amount": 65,
            "created_at": int(now.timestamp()),
        },
        "total_budget_currency_amount": final_budget_currency_amount,
    }
    mock_response = AsyncMock()
    mock_response.text = AsyncMock(return_value=json.dumps(vasp_response))
    mock_response.ok = True
    mock_pay_to_address.return_value.__aenter__.return_value = mock_response

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
    receiver_address = "$alice@uma.me"
    async with test_client.app.app_context():
        params = {
            "receiver": {"lud16": receiver_address},
            "sending_currency_code": "SAT",
            "sending_currency_amount": total_sending_amount,
        }
        request = await create_nip47_request_with_spending_limit("USD", 10000, params)
        response = await pay_to_address(access_token=token_hex(), request=request)

        params["budget_currency_code"] = "USD"
        params["receiver_address"] = params.pop("receiver")["lud16"]  # pyre-ignore[16]
        mock_pay_to_address.assert_called_once_with(
            url="/payments/lud16",
            data=PayToAddressRequest.from_dict(params).to_json(),
            headers=ANY,
        )
        mock_get_budget_estimate.assert_called_once_with(
            url="/budget_estimate",
            params={
                "sending_currency_code": "SAT",
                "sending_currency_amount": total_sending_amount,
                "budget_currency_code": "USD",
            },
            headers=ANY,
        )
        assert exclude_none_values(response.to_dict()) == vasp_response

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == final_budget_currency_amount
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == receiver_address
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == total_sending_amount
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
async def test_pay_to_address_payment_failed__sending_SAT_budget_USD(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
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
    mock_pay_to_address.return_value.__aenter__.return_value = mock_response

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
        total_sending_amount = 1000
        receiver_address = "$alice@uma.me"
        params = {
            "receiver": {"lud16": receiver_address},
            "sending_currency_code": "SAT",
            "sending_currency_amount": total_sending_amount,
        }
        request = await create_nip47_request_with_spending_limit("USD", 1000, params)

        with pytest.raises(Nip47RequestException):
            await pay_to_address(access_token=token_hex(), request=request)

            params["receiver_address"] = params.pop("receiver")[  # pyre-ignore[16]
                "lud16"
            ]
            mock_pay_to_address.assert_called_once_with(
                url="/payments/lud16",
                data=PayToAddressRequest.from_dict(params).to_json(),
                headers=ANY,
            )
            mock_get_budget_estimate.assert_called_once_with(
                url="/budget_estimate",
                params={
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": total_sending_amount,
                    "budget_currency_code": "USD",
                },
                headers=ANY,
            )

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0

        payment = (await db.session.execute(select(OutgoingPayment))).scalar_one()
        assert payment.receiver_type == ReceivingAddressType.LUD16
        assert payment.receiver == receiver_address
        assert payment.sending_currency_code == "SAT"
        assert payment.sending_currency_amount == total_sending_amount
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
async def test_budget_not_enough__sending_SAT_budget_USD(
    mock_get_budget_estimate: Mock, mock_pay_to_address: Mock, test_client: QuartClient
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
        total_sending_amount = 1000
        params = {
            "receiver": {"lud16": "$alice@uma.me"},
            "sending_currency_code": "SAT",
            "sending_currency_amount": total_sending_amount,
        }
        request = await create_nip47_request_with_spending_limit("USD", 100, params)

        with pytest.raises(InsufficientBudgetException):
            await pay_to_address(access_token=token_hex(), request=request)
            mock_pay_to_address.assert_not_called()
            mock_get_budget_estimate.assert_called_once_with(
                url="/budget_estimate",
                params={
                    "sending_currency_code": "SAT",
                    "sending_currency_amount": total_sending_amount,
                    "budget_currency_code": "USD",
                },
                headers=ANY,
            )

        spending_cycle = (await db.session.execute(select(SpendingCycle))).scalar_one()
        spending_limit = none_throws(request.nwc_connection.spending_limit)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == spending_limit.currency
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0
