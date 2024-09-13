# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging

from uma_auth.models.execute_quote_request import ExecuteQuoteRequest
from uma_auth.models.execute_quote_response import ExecuteQuoteResponse

from nwc_backend.event_handlers.input_validator import get_required_field
from nwc_backend.event_handlers.payment_utils import (
    create_spending_cycle_payment,
    update_on_payment_failed,
    update_on_payment_succeeded,
)
from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.spending_cycle_quote import SpendingCycleQuote
from nwc_backend.vasp_client import VaspUmaClient


async def execute_quote(
    access_token: str, request: Nip47Request
) -> ExecuteQuoteResponse:
    payment_hash = get_required_field(request.params, "payment_hash", str)
    quote = await SpendingCycleQuote.from_payment_hash(payment_hash)
    if not quote:
        raise InvalidInputException("Cannot recognize `payment_hash`.")

    payment = None
    budget_currency_code = None
    current_spending_limit = request.get_spending_limit()
    if current_spending_limit:
        payment = await create_spending_cycle_payment(
            access_token=access_token,
            request=request,
            sending_currency_code=quote.sending_currency_code,
            sending_currency_amount=quote.sending_currency_amount,
            spending_limit=current_spending_limit,
        )
        if current_spending_limit.currency_code != quote.sending_currency_code:
            budget_currency_code = current_spending_limit.currency_code

    try:
        response = await VaspUmaClient.instance().execute_quote(
            access_token=access_token,
            payment_hash=payment_hash,
            request=ExecuteQuoteRequest(budget_currency_code=budget_currency_code),
        )
        if payment:
            settled_budget_currency_amount = response.total_budget_currency_amount
            if not settled_budget_currency_amount:
                if payment.spending_cycle.limit_currency == quote.sending_currency_code:
                    settled_budget_currency_amount = quote.sending_currency_amount
                else:
                    logging.warning(
                        "Expected vasp to return total_budget_currency_amount on execute_quote request %s.",
                        request.id,
                    )
                    settled_budget_currency_amount = payment.estimated_amount
            await update_on_payment_succeeded(payment, settled_budget_currency_amount)
        return response
    except Exception:
        if payment:
            await update_on_payment_failed(payment)
        raise
