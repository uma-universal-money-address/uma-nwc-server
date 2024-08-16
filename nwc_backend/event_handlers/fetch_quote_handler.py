# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict


from uma_auth.models.quote import Quote

from nwc_backend.event_handlers.input_validator import get_required_field
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import (
    LockedCurrencySide,
    ReceivingAddress,
    VaspUmaClient,
)


async def fetch_quote(access_token: str, request: Nip47Request) -> Quote:
    sending_currency_code = get_required_field(
        request.params, "sending_currency_code", str
    )
    receiving_currency_code = get_required_field(
        request.params, "receiving_currency_code", str
    )
    locked_currency_amount = get_required_field(
        request.params, "locked_currency_amount", int
    )
    locked_currency_side = get_required_field(
        request.params, "locked_currency_side", LockedCurrencySide
    )
    receiver = get_required_field(request.params, "receiver", dict)
    receiving_address = ReceivingAddress.from_dict(receiver)
    return await VaspUmaClient.instance().fetch_quote(
        access_token=access_token,
        sending_currency_code=sending_currency_code,
        receiving_currency_code=receiving_currency_code,
        locked_currency_amount=locked_currency_amount,
        locked_currency_side=locked_currency_side,
        receiver_address=receiving_address,
    )
