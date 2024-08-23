# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict


from uma_auth.models.pay_keysend_request import PayKeysendRequest
from uma_auth.models.pay_keysend_response import PayKeysendResponse

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import VaspUmaClient


async def pay_keysend(access_token: str, request: Nip47Request) -> PayKeysendResponse:
    pay_keysend_request = PayKeysendRequest.from_dict(request.params)
    return await VaspUmaClient.instance().pay_keysend(
        access_token=access_token, request=pay_keysend_request
    )
