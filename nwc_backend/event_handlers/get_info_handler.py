# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def get_info(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    try:
        response = await VaspUmaClient.instance().get_info(access_token=access_token)
        return response.to_dict()
    except ClientResponseError as ex:
        logging.exception("Request get_info %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.OTHER, message=ex.message)
