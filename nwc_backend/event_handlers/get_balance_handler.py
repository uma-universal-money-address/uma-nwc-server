# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from uma_auth.models.get_balance_response import GetBalanceResponse

from nwc_backend.event_handlers.input_validator import get_optional_field
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def get_balance(access_token: str, request: Nip47Request) -> GetBalanceResponse:
    currency_code = get_optional_field(request.params, "currency_code", str)
    return await VaspUmaClient.instance().get_balance(
        access_token=access_token, currency_code=currency_code
    )
