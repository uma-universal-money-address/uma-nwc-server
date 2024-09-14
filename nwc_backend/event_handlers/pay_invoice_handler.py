# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
import math

from bolt11 import decode as bolt11_decode
from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse

from nwc_backend.event_handlers.payment_utils import (
    create_spending_cycle_payment,
    update_on_payment_failed,
    update_on_payment_succeeded,
)
from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
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
                    logging.warning(
                        "Expected vasp to return total_budget_currency_amount on pay_invoice request %s.",
                        request.id,
                    )
                    settled_budget_currency_amount = payment.estimated_amount
            await update_on_payment_succeeded(payment, settled_budget_currency_amount)
        return response
    except Exception:
        if payment:
            await update_on_payment_failed(payment)
        raise
