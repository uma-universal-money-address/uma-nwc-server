# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from copy import deepcopy
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error
from uma_auth.models.pay_to_address_request import PayToAddressRequest

from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import AddressType, ReceivingAddress, vasp_uma_client


async def pay_to_address(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    params = deepcopy(request.params)
    try:
        receiving_address = ReceivingAddress.from_dict(params["receiver"])
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
    params["receiver_address"] = receiving_address.address

    pay_to_address_request = PayToAddressRequest.from_dict(params)
    try:
        response = await vasp_uma_client.pay_to_address(
            access_token=access_token,
            request=pay_to_address_request,
            address_type=receiving_address.type,
        )
        return response.to_dict()
    except ClientResponseError as ex:
        logging.exception("Request pay_to_address %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.PAYMENT_FAILED, message=ex.message)
