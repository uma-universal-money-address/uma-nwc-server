# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from bolt11 import decode as bolt11_decode
from nostr_sdk import ErrorCode, Nip47Error

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import vasp_uma_client


async def lookup_invoice(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    payment_hash = None
    if request.params.get("payment_hash"):
        payment_hash = request.params["payment_hash"]

    if request.params.get("invoice"):
        if payment_hash:
            return Nip47Error(
                code=ErrorCode.OTHER,
                message="One of `payment_hash` or `invoice` is required, found both.",
            )
        try:
            payment_hash = bolt11_decode(request.params["invoice"]).payment_hash
        except Exception:
            return Nip47Error(
                code=ErrorCode.OTHER,
                message="Cannot decode `invoice`.",
            )

    if not payment_hash:
        return Nip47Error(
            code=ErrorCode.OTHER,
            message="One of `payment_hash` or `invoice` is required.",
        )

    try:
        response = await vasp_uma_client.lookup_invoice(
            access_token=access_token, payment_hash=payment_hash
        )
        return response.to_dict()
    except ClientResponseError as ex:
        if ex.status == 404:
            return Nip47Error(code=ErrorCode.NOT_FOUND, message=ex.message)

        logging.exception("Request lookup_invoice %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.OTHER, message=ex.message)
