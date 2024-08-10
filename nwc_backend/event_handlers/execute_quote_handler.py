# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import vasp_uma_client


async def execute_quote(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    try:
        response = await vasp_uma_client.execute_quote(
            access_token=access_token, payment_hash=request.params["payment_hash"]
        )
        return response.to_dict()
    except ClientResponseError as ex:
        logging.exception("Request execute_quote %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.PAYMENT_FAILED, message=ex.message)
