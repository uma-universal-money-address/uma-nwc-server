# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error
from uma_auth.models.make_invoice_request import MakeInvoiceRequest

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def make_invoice(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    make_invoice_request = MakeInvoiceRequest.from_dict(request.params)
    try:
        invoice = await VaspUmaClient.instance().make_invoice(
            access_token=access_token, request=make_invoice_request
        )
        return invoice.to_dict()
    except ClientResponseError as ex:
        logging.exception("Request make_invoice %s failed", str(request.id))
        # TODO: more granular error code
        return Nip47Error(code=ErrorCode.OTHER, message=ex.message)
