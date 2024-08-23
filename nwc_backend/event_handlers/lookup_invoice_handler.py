# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict


from bolt11 import decode as bolt11_decode
from uma_auth.models.transaction import Transaction

from nwc_backend.event_handlers.input_validator import get_optional_field
from nwc_backend.exceptions import InvalidInputException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def lookup_invoice(access_token: str, request: Nip47Request) -> Transaction:
    payment_hash = get_optional_field(request.params, "payment_hash", str)
    invoice = get_optional_field(request.params, "invoice", str)
    if payment_hash and invoice:
        raise InvalidInputException(
            "Only one of `payment_hash` or `invoice` is required, found both."
        )
    if not payment_hash and not invoice:
        raise InvalidInputException("One of `payment_hash` or `invoice` is required.")

    if not payment_hash:
        try:
            payment_hash = bolt11_decode(invoice).payment_hash
        except Exception:
            raise InvalidInputException("Cannot decode `invoice`.")

    return await VaspUmaClient.instance().lookup_invoice(
        access_token=access_token, payment_hash=payment_hash
    )
