# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from copy import deepcopy

from uma_auth.models.pay_to_address_request import PayToAddressRequest
from uma_auth.models.pay_to_address_response import PayToAddressResponse

from nwc_backend.event_handlers.input_validator import get_required_field
from nwc_backend.event_handlers.payment_utils import (
    create_outgoing_payment,
    update_on_payment_failed,
    update_on_payment_succeeded,
)
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.models.receiving_address import ReceivingAddressType
from nwc_backend.vasp_client import ReceivingAddress, VaspUmaClient


async def pay_to_address(
    access_token: str, request: Nip47Request
) -> PayToAddressResponse:
    params = deepcopy(request.params)
    receiver = get_required_field(params, "receiver", dict)
    receiving_address = ReceivingAddress.from_dict(receiver, ReceivingAddressType.LUD16)
    params.pop("receiver")
    params["receiver_address"] = receiving_address.address

    pay_to_address_request = PayToAddressRequest.from_dict(params)

    budget_currency = request.nwc_connection.budget_currency
    current_spending_limit = request.get_spending_limit()
    payment = await create_outgoing_payment(
        access_token=access_token,
        request=request,
        sending_currency_code=pay_to_address_request.sending_currency_code,
        sending_currency_amount=pay_to_address_request.sending_currency_amount,
        spending_limit=current_spending_limit,
        receiver=receiving_address.address,
        receiver_type=ReceivingAddressType.LUD16,
    )
    if budget_currency.code != pay_to_address_request.sending_currency_code:
        pay_to_address_request.budget_currency_code = budget_currency.code

    try:
        response = await VaspUmaClient.instance().pay_to_address(
            access_token=access_token,
            request=pay_to_address_request,
            address_type=receiving_address.type,
        )
        settled_budget_currency_amount = response.total_budget_currency_amount
        await update_on_payment_succeeded(
            request, payment, settled_budget_currency_amount
        )
        return response
    except Exception:
        await update_on_payment_failed(payment)
        raise
