# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error

from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import (
    AddressType,
    ReceivingAddress,
    VaspUmaClient,
)


async def lookup_user(
    access_token: str,
    request: Nip47Request,
    vasp_client: VaspUmaClient,
) -> dict[str, Any] | Nip47Error:
    receiver = request.params.get("receiver")
    if receiver is None:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message="Require `receiver` in the request params.",
        )

    try:
        receiving_address = ReceivingAddress.from_dict(receiver)
    except InvalidInputException as ex:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message=ex.error_message,
        )
    if receiving_address.type == AddressType.BOLT12:
        return Nip47Error(
            code=ErrorCode.NOT_IMPLEMENTED,
            message="Bolt12 is not yet supported.",
        )

    try:
        response = await vasp_client.lookup_user(
            access_token=access_token,
            receiving_address=receiving_address,
            base_sending_currency_code=request.params.get("base_sending_currency_code"),
        )
        return response.to_dict()
    except ClientResponseError as ex:
        if ex.status == 404:
            return Nip47Error(code=ErrorCode.NOT_FOUND, message=ex.message)

        logging.exception("Request lookup_user %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.OTHER, message=ex.message)
