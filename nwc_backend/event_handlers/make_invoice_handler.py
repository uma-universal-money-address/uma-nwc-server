# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from uma_auth.models.make_invoice_request import MakeInvoiceRequest
from uma_auth.models.transaction import Transaction

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import vasp_uma_client


async def make_invoice(access_token: str, request: Nip47Request) -> Transaction:
    make_invoice_request = MakeInvoiceRequest.from_dict(request.params)
    return await vasp_uma_client.make_invoice(
        access_token=access_token, request=make_invoice_request
    )
