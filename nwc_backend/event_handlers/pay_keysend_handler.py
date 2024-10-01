# pyre-strict

import math

from uma_auth.models.pay_keysend_request import PayKeysendRequest
from uma_auth.models.pay_keysend_response import PayKeysendResponse

from nwc_backend.event_handlers.payment_utils import (
    create_outgoing_payment,
    update_on_payment_failed,
    update_on_payment_succeeded,
)
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.receiving_address import ReceivingAddressType
from nwc_backend.vasp_client import VaspUmaClient


async def pay_keysend(access_token: str, request: Nip47Request) -> PayKeysendResponse:
    pay_keysend_request = PayKeysendRequest.from_dict(request.params)

    budget_currency = request.nwc_connection.budget_currency
    current_spending_limit = request.get_spending_limit()
    payment_amount_sats = math.ceil(pay_keysend_request.amount / 1000)
    payment = await create_outgoing_payment(
        access_token=access_token,
        request=request,
        sending_currency_code="SAT",
        sending_currency_amount=payment_amount_sats,
        spending_limit=current_spending_limit,
        receiver=pay_keysend_request.pubkey,
        receiver_type=ReceivingAddressType.NODE_PUBKEY,
    )
    if budget_currency.code != "SAT":
        pay_keysend_request.budget_currency_code = budget_currency.code

    try:
        response = await VaspUmaClient.instance().pay_keysend(
            access_token=access_token, request=pay_keysend_request
        )
        settled_budget_currency_amount = response.total_budget_currency_amount
        await update_on_payment_succeeded(
            request, payment, settled_budget_currency_amount
        )
        return response
    except Exception:
        await update_on_payment_failed(payment)
        raise
