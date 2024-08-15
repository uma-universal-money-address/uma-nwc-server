# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from uma_auth.models.get_info_response import GetInfoResponse

from nwc_backend.models.nip47_request import Nip47Request
from nwc_backend.vasp_client import vasp_uma_client


async def get_info(access_token: str, request: Nip47Request) -> GetInfoResponse:
    return await vasp_uma_client.get_info(access_token=access_token)
