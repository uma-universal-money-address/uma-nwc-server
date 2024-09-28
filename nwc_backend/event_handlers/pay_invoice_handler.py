# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import math

from bolt11 import decode as bolt11_decode
from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse

from nwc_backend.event_handlers.payment_utils import (
    create_outgoing_payment,
    update_on_payment_failed,
    update_on_payment_succeeded,
)
from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.receiving_address import ReceivingAddressType
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

    budget_currency = request.nwc_connection.budget_currency
    current_spending_limit = request.get_spending_limit()
    payment = await create_outgoing_payment(
        access_token=access_token,
        request=request,
        sending_currency_code="SAT",
        sending_currency_amount=payment_amount_sats,
        spending_limit=current_spending_limit,
        receiver=pay_invoice_request.invoice,
        receiver_type=ReceivingAddressType.BOLT11,
    )
    if budget_currency.code != "SAT":
        pay_invoice_request.budget_currency_code = budget_currency.code

    try:
        response = await VaspUmaClient.instance().pay_invoice(
            access_token=access_token, request=pay_invoice_request
        )
        settled_budget_currency_amount = response.total_budget_currency_amount
        await update_on_payment_succeeded(
            request, payment, settled_budget_currency_amount
        )
        return response
    except Exception:
        await update_on_payment_failed(payment)
        raise
