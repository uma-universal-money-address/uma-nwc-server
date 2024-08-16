# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict


from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode
from uma_auth.models.pay_invoice_request import PayInvoiceRequest
from uma_auth.models.pay_invoice_response import PayInvoiceResponse

from nwc_backend.exceptions import Nip47RequestException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def pay_invoice(access_token: str, request: Nip47Request) -> PayInvoiceResponse:
    pay_invoice_request = PayInvoiceRequest.from_dict(request.params)
    try:
        return await VaspUmaClient.instance().pay_invoice(
            access_token=access_token, request=pay_invoice_request
        )
    except ClientResponseError as ex:
        # TODO: more granular error code
        raise Nip47RequestException(
            error_code=ErrorCode.PAYMENT_FAILED, error_message=ex.message
        ) from ex
