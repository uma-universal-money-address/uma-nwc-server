# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import AddressType, ReceivingAddress, vasp_uma_client


async def lookup_user(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    receiver = request.get("receiver")
    if receiver is None:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message="Require receiver in the request params.",
        )

    if len(receiver) != 1:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message="Expect receiver to contain exactly one address.",
        )

    address_type, receiving_address = receiver.popitem()
    try:
        receiving_address = ReceivingAddress(
            address=receiving_address, type=AddressType(address_type)
        )
    except ValueError:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message="Expect receiver to contain address type bolt12 or lud16.",
        )

    try:
        response = await vasp_uma_client.lookup_user(
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
