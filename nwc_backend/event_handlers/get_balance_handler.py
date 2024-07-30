# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Any

from nostr_sdk import Nip47Error


async def get_balance(params: dict[str, Any]) -> dict[str, Any] | Nip47Error:
    raise NotImplementedError()
