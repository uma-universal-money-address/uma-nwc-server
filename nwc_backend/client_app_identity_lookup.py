# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from nostr_sdk import (
    Client,
    Event,
    Filter,
    Kind,
    KindEnum,
    Metadata,
    PublicKey,
    verify_nip05,
)

from nwc_backend.exceptions import InvalidClientIdException


class Nip05VerificationStatus(Enum):
    VERIFIED = "VERIFIED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


@dataclass
class Nip05:
    domain: str
    verification_status: Nip05VerificationStatus

    @classmethod
    async def from_nip05_address(
        cls, nip05_address: Optional[str], pubkey: PublicKey
    ) -> Optional["Nip05"]:
        if not nip05_address:
            return None

        if "@" in nip05_address:
            [_, domain] = nip05_address.split("@")
        else:
            domain = nip05_address

        return Nip05(
            domain=domain, verification_status=await cls.verify(nip05_address, pubkey)
        )

    @classmethod
    async def verify(
        cls, nip05_address: str, pubkey: PublicKey
    ) -> Nip05VerificationStatus:
        try:
            verified = await verify_nip05(public_key=pubkey, nip05=nip05_address)
        except Exception:
            return Nip05VerificationStatus.UNKNOWN

        return (
            Nip05VerificationStatus.VERIFIED
            if verified
            else Nip05VerificationStatus.INVALID
        )


@dataclass
class ClientAppInfo:
    pubkey: PublicKey
    identity_relay: str
    name: Optional[str]
    image_url: Optional[str]
    nip05: Optional[Nip05]
    display_name: Optional[str]
    allowed_redirect_urls: Optional[list[str]]


async def look_up_client_app_identity(client_id: str) -> Optional[ClientAppInfo]:
    try:
        [client_pubkey, relay_url] = client_id.split(" ")
    except ValueError:
        raise InvalidClientIdException(
            "Invalid client_id. Should be in the format <npub> <relay>."
        )

    if not relay_url.startswith("wss://") and not relay_url.startswith("ws://"):
        raise InvalidClientIdException("Invalid relay url in client_id.")

    try:
        client_pubkey = PublicKey.parse(client_pubkey)
    except Exception:
        raise InvalidClientIdException("Invalid public key in client_id.")

    client = Client()
    await client.add_relay(relay_url)
    await client.connect()

    filter = (
        Filter()
        .author(client_pubkey)
        .kinds(
            [
                Kind.from_enum(KindEnum.METADATA()),  # pyre-ignore[6]
                # update it with 13195
                Kind.from_enum(KindEnum.AUTHENTICATION()),  # pyre-ignore[6]
            ]
        )
        .limit(2)
    )
    events = await client.get_events_of(filters=[filter], timeout=None)  # pyre-ignore
    await client.disconnect()

    if not events:
        logging.debug("No identity metadata found for client app %s", client_id)
        return None

    client_app_info = await _look_up_from_kind_13195(
        events=events, client_pubkey=client_pubkey, relay_url=relay_url
    )
    if client_app_info:
        logging.debug("Found 13195 for client_id %s", client_id)
        return client_app_info

    logging.debug("Found 0 for client_id %s", client_id)
    return await _look_up_from_kind_0(
        events=events, client_pubkey=client_pubkey, relay_url=relay_url
    )


async def _look_up_from_kind_13195(
    events: list[Event], client_pubkey: PublicKey, relay_url: str
) -> Optional[ClientAppInfo]:
    events_13195 = [event for event in events if event.kind().as_u16 == 13195]
    if events_13195:
        event = events_13195[0]
        event.verify_signature()
        content = json.loads(event.content())
        return ClientAppInfo(
            pubkey=client_pubkey,
            identity_relay=relay_url,
            name=content.get("name"),
            image_url=content.get("image"),
            nip05=await Nip05.from_nip05_address(
                nip05_address=content.get("nip05"), pubkey=client_pubkey
            ),
            display_name=content.get("name"),
            allowed_redirect_urls=content.get("allowed_redirect_urls"),
        )
    return None


async def _look_up_from_kind_0(
    events: list[Event], client_pubkey: PublicKey, relay_url: str
) -> ClientAppInfo:
    [event] = [
        event for event in events if event.kind().as_enum() == KindEnum.METADATA()
    ]
    event.verify_signature()
    metadata = Metadata.from_json(event.content())
    return ClientAppInfo(
        pubkey=client_pubkey,
        identity_relay=relay_url,
        name=metadata.get_name(),
        image_url=metadata.get_picture(),
        nip05=await Nip05.from_nip05_address(
            nip05_address=metadata.get_nip05(), pubkey=client_pubkey
        ),
        display_name=metadata.get_display_name(),
        allowed_redirect_urls=None,
    )
