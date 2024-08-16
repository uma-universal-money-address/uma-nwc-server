# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from copy import deepcopy

from aiohttp import ClientResponseError
from nostr_sdk import ErrorCode
from uma_auth.models.pay_to_address_request import PayToAddressRequest
from uma_auth.models.pay_to_address_response import PayToAddressResponse

from nwc_backend.event_handlers.input_validator import get_required_field
from nwc_backend.exceptions import Nip47RequestException
from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import ReceivingAddress, VaspUmaClient


async def pay_to_address(
    access_token: str, request: Nip47Request
) -> PayToAddressResponse:
    params = deepcopy(request.params)
    receiver = get_required_field(params, "receiver", dict)
    receiving_address = ReceivingAddress.from_dict(receiver)
    params.pop("receiver")
    params["receiver_address"] = receiving_address.address

    pay_to_address_request = PayToAddressRequest.from_dict(params)
    try:
        return await VaspUmaClient.instance().pay_to_address(
            access_token=access_token,
            request=pay_to_address_request,
            address_type=receiving_address.type,
        )
    except ClientResponseError as ex:
        # TODO: more granular error code
        raise Nip47RequestException(
            error_code=ErrorCode.PAYMENT_FAILED, error_message=ex.message
        ) from ex
