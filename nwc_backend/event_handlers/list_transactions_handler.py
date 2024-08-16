# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from uma_auth.models.list_transactions_response import ListTransactionsResponse
from uma_auth.models.transaction import TransactionType

from nwc_backend.event_handlers.input_validator import get_optional_field
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def list_transactions(
    access_token: str, request: Nip47Request
) -> ListTransactionsResponse:
    return await VaspUmaClient.instance().list_transactions(
        access_token=access_token,
        from_timestamp=get_optional_field(request.params, "from", int),
        until_timestamp=get_optional_field(request.params, "until", int),
        limit=get_optional_field(request.params, "limit", int),
        offset=get_optional_field(request.params, "offset", int),
        unpaid=get_optional_field(request.params, "unpaid", bool),
        type=get_optional_field(request.params, "type", TransactionType),
    )
