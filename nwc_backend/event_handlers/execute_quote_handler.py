# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from uma_auth.models.execute_quote_response import ExecuteQuoteResponse

from nwc_backend.event_handlers.input_validator import get_required_field
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def execute_quote(
    access_token: str, request: Nip47Request
) -> ExecuteQuoteResponse:
    return await VaspUmaClient.instance().execute_quote(
        access_token=access_token,
        payment_hash=get_required_field(request.params, "payment_hash", str),
    )
