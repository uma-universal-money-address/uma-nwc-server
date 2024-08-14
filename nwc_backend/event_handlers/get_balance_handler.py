# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def get_balance(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    try:
        response = await VaspUmaClient.instance().get_balance(
            access_token=access_token, currency_code=request.params.get("currency_code")
        )
        return response.to_dict()
    except ClientResponseError as ex:
        logging.exception("Request get_balance %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.OTHER, message=ex.message)
