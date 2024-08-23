# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from uma_auth.models.lookup_user_response import LookupUserResponse

from nwc_backend.event_handlers.input_validator import (
    get_optional_field,
    get_required_field,
)
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import ReceivingAddress, VaspUmaClient


async def lookup_user(access_token: str, request: Nip47Request) -> LookupUserResponse:
    receiver = get_required_field(request.params, "receiver", dict)
    receiver_address = ReceivingAddress.from_dict(receiver)
    base_sending_currency_code = get_optional_field(
        request.params, "base_sending_currency_code", str
    )
    return await VaspUmaClient().lookup_user(
        access_token=access_token,
        receiver_address=receiver_address,
        base_sending_currency_code=base_sending_currency_code,
    )
