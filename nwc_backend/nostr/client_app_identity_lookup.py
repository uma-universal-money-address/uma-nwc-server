# pyre-strict

import json
import logging
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Callable, List, Optional
from urllib.parse import urlparse

from nostr_sdk import (
    Alphabet,
    Client,
    Event,
    EventSource,
    Filter,
    Kind,
    KindEnum,
    Metadata,
    Nip19Profile,
    PublicKey,
    SingleLetterTag,
    TagKind,
    verify_nip05,
)
from quart import current_app

from nwc_backend.exceptions import InvalidClientIdException


class Nip05VerificationStatus(Enum):
    VERIFIED = "VERIFIED"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class Nip68VerificationStatus(Enum):
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"
    NONE = "NONE"


@dataclass
class Nip68Verification:
    status: Nip68VerificationStatus
    authority_pubkey: str
    authority_name: str
    revoked_at: Optional[int]


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
    name: Optional[str] = None
    image_url: Optional[str] = None
    nip05: Optional[Nip05] = None
    display_name: Optional[str] = None
    allowed_redirect_urls: Optional[list[str]] = None
    app_authority_verification: Optional[Nip68Verification] = None

    def is_redirect_url_allowed(self, redirect_url: str) -> bool:
        if not self.allowed_redirect_urls:
            return True

        parsed_redirect_url = urlparse(redirect_url)
        for allowed_redirect_url in self.allowed_redirect_urls:  # pyre-ignore[16]
            parsed_allowed_redirect_url = urlparse(allowed_redirect_url)
            if (
                parsed_redirect_url.scheme,
                parsed_redirect_url.netloc,
                parsed_redirect_url.path,
            ) == (
                parsed_allowed_redirect_url.scheme,
                parsed_allowed_redirect_url.netloc,
                parsed_allowed_redirect_url.path,
            ):
                return True
        return False


async def look_up_client_app_identity(
    client_id: str,
    nostr_client_factory: Callable[[], Client] = Client,
) -> Optional[ClientAppInfo]:
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

    client = nostr_client_factory()
    await client.add_relay(relay_url)
    await client.connect()

    filter = (
        Filter()
        .author(client_pubkey)
        .kinds(
            [
                Kind.from_enum(KindEnum.METADATA()),  # pyre-ignore[6]
                Kind(kind=13195),
            ]
        )
        .limit(2)
    )
    source = EventSource.relays(timeout=timedelta(seconds=20))
    events = await client.get_events_of(filters=[filter], source=source)
    await client.disconnect()

    if not events:
        logging.debug("No identity metadata found for client app %s", client_id)
        return None

    client_app_info = await _look_up_from_kind_13195(
        events=events,
        client_pubkey=client_pubkey,
        relay_url=relay_url,
        nostr_client_factory=nostr_client_factory,
    )
    if client_app_info:
        logging.debug("Found 13195 for client_id %s", client_id)
        return client_app_info

    logging.debug("Found 0 for client_id %s", client_id)
    return await _look_up_from_kind_0(
        events=events, client_pubkey=client_pubkey, relay_url=relay_url
    )


async def _look_up_from_kind_13195(
    events: List[Event],
    client_pubkey: PublicKey,
    relay_url: str,
    nostr_client_factory: Callable[[], Client],
) -> Optional[ClientAppInfo]:
    events_13195 = [event for event in events if event.kind().as_u16() == 13195]
    if not events_13195:
        return None

    event = events_13195[0]
    if not event.verify_signature():
        raise InvalidClientIdException("Invalid signature in 13195 event.")

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
        app_authority_verification=await _check_app_authorities(
            event, nostr_client_factory
        ),
    )


async def _look_up_from_kind_0(
    events: list[Event], client_pubkey: PublicKey, relay_url: str
) -> ClientAppInfo:
    [event] = [
        event for event in events if event.kind().as_enum() == KindEnum.METADATA()
    ]

    if not event.verify_signature():
        raise InvalidClientIdException("Invalid signature in metadata event.")

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
        app_authority_verification=None,
    )


async def _check_app_authorities(
    identity_event: Event,
    nostr_client_factory: Callable[[], Client] = Client,
) -> Optional[Nip68Verification]:
    registration_authorities = current_app.config.get("CLIENT_APP_AUTHORITIES")
    if not registration_authorities:
        return None

    try:
        authority_nprofiles = [
            Nip19Profile.from_bech32(authority)
            for authority in registration_authorities
        ]
    except Exception:
        logging.exception("Invalid NIP19 profile in CLIENT_APP_AUTHORITIES.")
        return None

    client = nostr_client_factory()
    for nprofile in authority_nprofiles:
        for relay in nprofile.relays():
            await client.add_read_relay(relay)

    authority_pubkeys = [nprofile.public_key() for nprofile in authority_nprofiles]

    await client.connect()
    label_filter = (
        Filter()
        .authors(authority_pubkeys)
        .kinds(
            [
                Kind.from_enum(KindEnum.LABEL()),  # pyre-ignore[6]
                Kind.from_enum(KindEnum.METADATA()),  # pyre-ignore[6]
            ]
        )
        .custom_tag(SingleLetterTag.uppercase(Alphabet.L), ["nip68.client_app"])
        .event(identity_event.id())
    )
    metadata_filter = (
        Filter()
        .authors(authority_pubkeys)
        .kinds(
            [
                Kind.from_enum(KindEnum.METADATA()),  # pyre-ignore[6]
            ]
        )
    )
    source = EventSource.relays(timeout=timedelta(seconds=10))
    verification_and_metadata_events = await client.get_events_of(
        filters=[label_filter, metadata_filter], source=source
    )
    await client.disconnect()

    verification_events = [
        event
        for event in verification_and_metadata_events
        if event.kind().as_enum() == KindEnum.LABEL()
    ]

    metadata_events_by_pubkey: dict[str, Event] = {
        event.author().to_hex(): event
        for event in verification_and_metadata_events
        if event.kind().as_enum() == KindEnum.METADATA()
    }

    def authority_name_for_pubkey(pubkey: str) -> str:
        authority_name = "Default App Authority"
        if metadata_events_by_pubkey.get(pubkey):
            authority_name = (
                Metadata.from_json(
                    metadata_events_by_pubkey[pubkey].content()
                ).get_name()
                or authority_name
            )
        return authority_name

    # If any verifications were revoked, prioritize that status above all others.
    for event in verification_events:
        status = event.get_tag_content(
            # pyre-ignore[6]
            TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.L))
        )
        if status and status.lower() == "revoked":
            return Nip68Verification(
                status=Nip68VerificationStatus.REVOKED,
                authority_pubkey=event.author().to_hex(),
                authority_name=authority_name_for_pubkey(event.author().to_hex()),
                revoked_at=event.created_at().as_secs(),
            )

    # If any verifications were confirmed, return the first one.
    for event in verification_events:
        status = event.get_tag_content(
            # pyre-ignore[6]
            TagKind.SINGLE_LETTER(SingleLetterTag.lowercase(Alphabet.L))
        )
        if status and status.lower() == "verified":
            return Nip68Verification(
                status=Nip68VerificationStatus.VERIFIED,
                authority_pubkey=event.author().to_hex(),
                authority_name=authority_name_for_pubkey(event.author().to_hex()),
                revoked_at=None,
            )

    return None
