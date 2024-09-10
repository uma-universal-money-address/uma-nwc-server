# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
import math

from uma_auth.models.pay_keysend_request import PayKeysendRequest
from uma_auth.models.pay_keysend_response import PayKeysendResponse

from nwc_backend.event_handlers.payment_utils import (
    create_spending_cycle_payment,
    update_on_payment_failed,
    update_on_payment_succeeded,
)
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def pay_keysend(access_token: str, request: Nip47Request) -> PayKeysendResponse:
    pay_keysend_request = PayKeysendRequest.from_dict(request.params)

    payment = None
    current_spending_limit = request.get_spending_limit()
    payment_amount_sats = math.ceil(pay_keysend_request.amount / 1000)
    if current_spending_limit:
        payment = await create_spending_cycle_payment(
            access_token=access_token,
            request=request,
            sending_currency_code="SAT",
            sending_currency_amount=payment_amount_sats,
            spending_limit=current_spending_limit,
        )
        if current_spending_limit.currency_code != "SAT":
            pay_keysend_request.budget_currency_code = (
                current_spending_limit.currency_code
            )

    try:
        response = await VaspUmaClient.instance().pay_keysend(
            access_token=access_token, request=pay_keysend_request
        )
        if payment:
            settled_budget_currency_amount = response.total_budget_currency_amount
            if not settled_budget_currency_amount:
                if payment.spending_cycle.limit_currency == "SAT":
                    settled_budget_currency_amount = payment_amount_sats
                else:
                    logging.debug(
                        "Expect vasp to return total_budget_currency_amount on pay_keysend request %s.",
                        request.id,
                    )
                    settled_budget_currency_amount = payment.estimated_amount
            await update_on_payment_succeeded(payment, settled_budget_currency_amount)
        return response
    except Exception:
        if payment:
            await update_on_payment_failed(payment)
        raise
