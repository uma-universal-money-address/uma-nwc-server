# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
import math
from typing import Optional
from uuid import uuid4

from quart import current_app

from nwc_backend.db import db
from nwc_backend.exceptions import InsufficientBudgetException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.outgoing_payment import (
    OutgoingPayment,
    PaymentStatus,
    ReceivingAddressType,
)
from nwc_backend.models.payment_quote import PaymentQuote
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.typing import none_throws
from nwc_backend.vasp_client import VaspUmaClient


async def update_on_payment_succeeded(
    request: Nip47Request,
    payment: OutgoingPayment,
    settled_budget_currency_amount: Optional[int],
) -> None:
    payment.status = PaymentStatus.SUCCEEDED
    if not settled_budget_currency_amount:
        settled_budget_currency_amount = (
            _get_settled_budget_currency_amount_from_payment(request, payment)
        )
    payment.settled_budget_currency_amount = settled_budget_currency_amount

    if payment.spending_cycle:
        spending_cycle = await db.session.get_one(
            SpendingCycle, payment.spending_cycle_id, with_for_update=True
        )
        spending_cycle.total_spent_on_hold -= none_throws(payment.budget_on_hold)
        spending_cycle.total_spent += none_throws(settled_budget_currency_amount)

    await db.session.commit()


async def update_on_payment_failed(payment: OutgoingPayment) -> None:
    payment.status = PaymentStatus.FAILED
    if payment.spending_cycle:
        spending_cycle = await db.session.get_one(
            SpendingCycle, payment.spending_cycle_id, with_for_update=True
        )
        spending_cycle.total_spent_on_hold -= none_throws(payment.budget_on_hold)
    await db.session.commit()


def get_budget_buffer_multiplier() -> float:
    return current_app.config.get("BUDGET_BUFFER_MULTIPLIER") or 1


async def create_outgoing_payment(
    access_token: str,
    request: Nip47Request,
    receiver: str,
    receiver_type: ReceivingAddressType,
    sending_currency_code: str,
    sending_currency_amount: int,
    spending_limit: Optional[SpendingLimit],
    quote: Optional[PaymentQuote] = None,
) -> OutgoingPayment:
    payment = OutgoingPayment(
        id=uuid4(),
        nip47_request_id=request.id,
        nwc_connection_id=request.nwc_connection_id,
        sending_currency_code=sending_currency_code,
        sending_currency_amount=sending_currency_amount,
        status=PaymentStatus.PENDING,
        quote_id=quote.id if quote else None,
        receiver=receiver,
        receiver_type=receiver_type,
    )
    budget_currency = request.nwc_connection.budget_currency
    if spending_limit:
        spending_cycle = await spending_limit.get_or_create_current_spending_cycle()
        if spending_cycle.get_available_budget_amount() == 0:
            raise InsufficientBudgetException()

        if budget_currency.code == sending_currency_code:
            estimated_budget_currency_amount = sending_currency_amount
        else:
            budget_estimate_response = (
                await VaspUmaClient.instance().get_budget_estimate(
                    access_token=access_token,
                    sending_currency_code=sending_currency_code,
                    sending_currency_amount=sending_currency_amount,
                    budget_currency_code=budget_currency.code,
                )
            )
            estimated_budget_currency_amount = (
                budget_estimate_response.estimated_budget_currency_amount
            )

        budget_buffer_multiplier = get_budget_buffer_multiplier()
        budget_on_hold = math.ceil(
            estimated_budget_currency_amount * budget_buffer_multiplier
        )

        spending_cycle = await db.session.get_one(
            SpendingCycle, spending_cycle.id, with_for_update=True
        )
        if not spending_cycle.can_make_payment(budget_on_hold):
            raise InsufficientBudgetException()

        payment.spending_cycle = spending_cycle
        payment.estimated_budget_currency_amount = estimated_budget_currency_amount
        payment.budget_on_hold = budget_on_hold
        spending_cycle.total_spent_on_hold += budget_on_hold

    db.session.add(payment)
    await db.session.commit()
    return payment


def _get_settled_budget_currency_amount_from_payment(
    request: Nip47Request, payment: OutgoingPayment
) -> Optional[int]:
    budget_currency = request.nwc_connection.budget_currency
    if budget_currency.code == payment.sending_currency_code:
        return payment.sending_currency_amount
    else:
        logging.error(
            "Expected vasp to return total_budget_currency_amount in %s request %s.",
            request.method.name,
            request.id,
        )
        return payment.estimated_budget_currency_amount
