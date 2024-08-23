# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def pay_invoice(access_token: str, request: Nip47Request) -> PayInvoiceResponse:
    pay_invoice_request = PayInvoiceRequest.from_dict(request.params)
    return await VaspUmaClient.instance().pay_invoice(
        access_token=access_token, request=pay_invoice_request
    )
