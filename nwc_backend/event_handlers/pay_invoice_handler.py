# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
from typing import Any

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode, Nip47Error
from uma_auth.models.pay_invoice_request import PayInvoiceRequest

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import vasp_uma_client


async def pay_invoice(
    access_token: str, request: Nip47Request
) -> dict[str, Any] | Nip47Error:
    pay_invoice_request = PayInvoiceRequest.from_dict(request.params)
    try:
        response = await vasp_uma_client.pay_invoice(
            access_token=access_token, request=pay_invoice_request
        )
        return response.to_dict()
    except ClientResponseError as ex:
        logging.exception("Request pay_invoice %s failed", str(request.id))
        return Nip47Error(code=ErrorCode.PAYMENT_FAILED, message=ex.message)
