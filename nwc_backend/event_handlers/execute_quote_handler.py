# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode
from uma_auth.models.execute_quote_response import ExecuteQuoteResponse

from nwc_backend.event_handlers.input_validator import get_required_field
from nwc_backend.exceptions import Nip47RequestException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def execute_quote(
    access_token: str, request: Nip47Request
) -> ExecuteQuoteResponse:
    try:
        return await VaspUmaClient.instance().execute_quote(
            access_token=access_token,
            payment_hash=get_required_field(request.params, "payment_hash", str),
        )
    except ClientResponseError as ex:
        # TODO: more granular error code
        raise Nip47RequestException(
            error_code=ErrorCode.PAYMENT_FAILED, error_message=ex.message
        ) from ex
