# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error

from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import (
    LockedCurrencySide,
    ReceivingAddress,
    vasp_uma_client,
)


async def fetch_quote(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:

    try:
        locked_currency_side = LockedCurrencySide(
            request.params["locked_currency_side"].lower()
        )
    except ValueError:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message="Expect locked_currency_side to be either sending or receiving.",
        )

    try:
        receiving_address = ReceivingAddress.from_dict(
            request.params["receiving_address"], "receiving_address"
        )
    except InvalidInputException as ex:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message=ex.error_message,
        )

    try:
        response = await vasp_uma_client.fetch_quote(
            access_token=access_token,
            sending_currency_code=request.params["sending_currency_code"],
            receiving_currency_code=request.params["receiving_currency_code"],
            locked_currency_amount=request.params["locked_currency_amount"],
            locked_currency_side=locked_currency_side,
            receiving_address=receiving_address,
        )
        return response.to_dict()
    except ClientResponseError as ex:
        logging.exception("Request fetch_quote %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.OTHER, message=ex.message)
