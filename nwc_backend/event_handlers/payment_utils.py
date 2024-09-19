# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import math
from uuid import uuid4

from quart import current_app

from nwc_backend.db import db
from nwc_backend.exceptions import InsufficientBudgetException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_cycle_payment import (
    PaymentStatus,
    SpendingCyclePayment,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.vasp_client import VaspUmaClient


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
    spending_cycle = await spending_limit.get_or_create_current_spending_cycle()
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
