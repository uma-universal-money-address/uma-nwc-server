# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
import math
from uuid import uuid4

from bolt11 import decode as bolt11_decode
from quart import current_app
from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse

from nwc_backend.db import db
from nwc_backend.exceptions import InsufficientBudgetException, InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_cycle_payment import (
    PaymentStatus,
    SpendingCyclePayment,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.vasp_client import VaspUmaClient


async def pay_invoice(access_token: str, request: Nip47Request) -> PayInvoiceResponse:
    pay_invoice_request = PayInvoiceRequest.from_dict(request.params)

    payment_amount_msats = pay_invoice_request.amount
    if not pay_invoice_request.amount:
        payment_amount_msats = bolt11_decode(pay_invoice_request.invoice).amount_msat
    if not payment_amount_msats:
        raise InvalidInputException(
            "Expect to have `amount` set for zero-amount invoice."
        )

    payment_amount_sats = math.ceil(payment_amount_msats / 1000)

    payment = None
    current_spending_limit = request.get_spending_limit()
    if current_spending_limit:
        payment = await create_spending_cycle_payment(
            access_token=access_token,
            request=request,
            sending_currency_code="SAT",
            sending_currency_amount=payment_amount_sats,
            spending_limit=current_spending_limit,
        )
        if current_spending_limit.currency_code != "SAT":
            pay_invoice_request.budget_currency_code = (
                current_spending_limit.currency_code
            )

    try:
        response = await VaspUmaClient.instance().pay_invoice(
            access_token=access_token, request=pay_invoice_request
        )
        if payment:
            settled_budget_currency_amount = response.total_budget_currency_amount
            if not settled_budget_currency_amount:
                if payment.spending_cycle.limit_currency == "SAT":
                    settled_budget_currency_amount = payment_amount_sats
                else:
                    logging.debug(
                        "Expect vasp to return total_budget_currency_amount on pay_invoice request %s.",
                        request.id,
                    )
                    settled_budget_currency_amount = payment.estimated_amount
            await update_on_payment_succeeded(payment, settled_budget_currency_amount)
        return response
    except Exception:
        if payment:
            await update_on_payment_failed(payment)
        raise


async def update_on_payment_succeeded(
    payment: SpendingCyclePayment, settled_budget_currency_amount: int
) -> None:
    spending_cycle = await db.session.get_one(
        SpendingCycle, payment.spending_cycle_id, with_for_update=True
    )
    payment.status = PaymentStatus.SUCCEEDED
    payment.settled_amount = settled_budget_currency_amount
    spending_cycle.total_spent_on_hold -= payment.budget_on_hold
    spending_cycle.total_spent += settled_budget_currency_amount
    await db.session.commit()


async def update_on_payment_failed(payment: SpendingCyclePayment) -> None:
    spending_cycle = await db.session.get_one(
        SpendingCycle, payment.spending_cycle_id, with_for_update=True
    )
    payment.status = PaymentStatus.FAILED
    spending_cycle.total_spent_on_hold -= payment.budget_on_hold
    await db.session.commit()


def get_budget_buffer_multiplier() -> float:
    return current_app.config.get("BUDGET_BUFFER_MULTIPLIER") or 1


async def create_spending_cycle_payment(
    access_token: str,
    request: Nip47Request,
    sending_currency_code: str,
    sending_currency_amount: int,
    spending_limit: SpendingLimit,
) -> SpendingCyclePayment:
    spending_cycle = await spending_limit.get_current_spending_cycle()
    if spending_cycle.get_available_budget_amount() == 0:
        raise InsufficientBudgetException()

    if spending_cycle.limit_currency == sending_currency_code:
        estimated_budget_currency_amount = sending_currency_amount
    else:
        budget_estimate_response = await VaspUmaClient.instance().get_budget_estimate(
            access_token=access_token,
            sending_currency_code=sending_currency_code,
            sending_currency_amount=sending_currency_amount,
            budget_currency_code=spending_cycle.limit_currency,
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

    payment = SpendingCyclePayment(
        id=uuid4(),
        nip47_request_id=request.id,
        spending_cycle=spending_cycle,
        estimated_amount=estimated_budget_currency_amount,
        budget_on_hold=budget_on_hold,
        status=PaymentStatus.PENDING,
    )
    spending_cycle.total_spent_on_hold += budget_on_hold
    db.session.add(payment)
    await db.session.commit()
    return payment
