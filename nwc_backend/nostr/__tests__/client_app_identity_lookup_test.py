import json
from typing import List
from unittest.mock import AsyncMock, patch

from nostr_sdk import (
    EventBuilder,
    EventSource,
    Filter,
    Keys,
    Kind,
    KindEnum,
    Metadata,
    Tag,
)
from quart.app import QuartClient

from nwc_backend.nostr.__tests__.fake_nostr_client import FakeNostrClient
from nwc_backend.nostr.client_app_identity_lookup import (
    Nip05,
    Nip05VerificationStatus,
    Nip68VerificationStatus,
    look_up_client_app_identity,
)

CLIENT_PUBKEY = "npub13msd7fakpaqerq036kk0c6pf9effz5nn5yk6nqj4gtwtzr5l6fxq64z8x5"
CLIENT_PRIVKEY = "nsec1e792rulwmsjanw783x39r8vcm23c2hwcandwahaw6wh39rfydshqxhfm7x"
CLIENT_ID = f"{CLIENT_PUBKEY} wss://nos.lol"

AUTHORITY_PUBKEY = "npub1k3tqgywqfv2djgrf9a0m6utx94am5uykw7hhege8g3t3vzdl6scq6ewt9d"
AUTHORITY_PRIVKEY = "nsec1gn4guugvc8656dwqs3j486leffaepx2mvpym7qkh2k2vuuextvtsnv6x76"


async def test_unregistered(test_client: QuartClient) -> None:
    fake_client = FakeNostrClient()

    async def on_get_events(filters: List[Filter], source: EventSource):
        return []

    fake_client.on_get_events = on_get_events
    identity = await look_up_client_app_identity(
        client_id=CLIENT_ID,
        nostr_client_factory=lambda: fake_client,
    )

    assert identity is None


@patch.object(Nip05, "verify", new_callable=AsyncMock)
async def test_only_kind0(
    mock_verify_nip05: AsyncMock, test_client: QuartClient
) -> None:
    mock_verify_nip05.return_value = Nip05VerificationStatus.VERIFIED
    fake_client = FakeNostrClient()

    async def on_get_events(filters: List[Filter], source: EventSource):
        return [
            EventBuilder.metadata(
                Metadata()
                .set_name("Blue Drink")
                .set_nip05("_@bluedrink.com")
                .set_picture("https://bluedrink.com/image.png")
            ).to_event(Keys.parse(CLIENT_PRIVKEY))
        ]

    fake_client.on_get_events = on_get_events
    identity = await look_up_client_app_identity(
        client_id=CLIENT_ID,
        nostr_client_factory=lambda: fake_client,
    )

    mock_verify_nip05.assert_called_once()

    assert identity is not None
    assert identity.name == "Blue Drink"
    assert identity.nip05 is not None
    assert identity.nip05.verification_status == Nip05VerificationStatus.VERIFIED
    assert identity.image_url == "https://bluedrink.com/image.png"


@patch.object(Nip05, "verify", new_callable=AsyncMock)
async def test_only_kind13195_no_label(
    mock_verify_nip05: AsyncMock, test_client: QuartClient
) -> None:
    mock_verify_nip05.return_value = Nip05VerificationStatus.VERIFIED
    fake_client = FakeNostrClient()

    async def on_get_events(filters: List[Filter], source: EventSource):
        return [
            EventBuilder(
                kind=Kind(13195),
                content=json.dumps(
                    {
                        "name": "Green Drink",
                        "nip05": "_@greendrink.com",
                        "image": "https://greendrink.com/image.png",
                        "allowed_redirect_urls": ["https://greendrink.com/callback"],
                    }
                ),
                tags=[],
            ).to_event(Keys.parse(CLIENT_PRIVKEY))
        ]

    fake_client.on_get_events = on_get_events
    async with test_client.app.app_context():
        identity = await look_up_client_app_identity(
            client_id=CLIENT_ID,
            nostr_client_factory=lambda: fake_client,
        )

    mock_verify_nip05.assert_called_once()

    assert identity is not None
    assert identity.name == "Green Drink"
    assert identity.nip05 is not None
    assert identity.nip05.verification_status == Nip05VerificationStatus.VERIFIED
    assert identity.image_url == "https://greendrink.com/image.png"
    assert identity.allowed_redirect_urls == ["https://greendrink.com/callback"]
    assert identity.app_authority_verification is None


@patch.object(Nip05, "verify", new_callable=AsyncMock)
async def test_only_kind13195_with_label(
    mock_verify_nip05: AsyncMock, test_client: QuartClient
) -> None:
    mock_verify_nip05.return_value = Nip05VerificationStatus.VERIFIED
    fake_client = FakeNostrClient()

    id_event = EventBuilder(
        kind=Kind(13195),
        content=json.dumps(
            {
                "name": "Green Drink",
                "nip05": "_@greendrink.com",
                "image": "https://greendrink.com/image.png",
                "allowed_redirect_urls": ["https://greendrink.com/callback"],
            }
        ),
        tags=[],
    ).to_event(Keys.parse(CLIENT_PRIVKEY))

    async def on_get_events(filters: List[Filter], source: EventSource):
        filter_kinds = filters[0].as_record().kinds or []
        if Kind(13195) in filter_kinds:
            return [id_event]
        if Kind.from_enum(KindEnum.LABEL()) in filter_kinds:  # pyre-ignore[6]
            return [
                EventBuilder.label("nip68.client_app", ["verified", "nip68.client_app"])
                .add_tags([Tag.event(id_event.id())])
                .to_event(Keys.parse(AUTHORITY_PRIVKEY)),
                EventBuilder.metadata(
                    Metadata().set_name("Important Authority")
                ).to_event(Keys.parse(AUTHORITY_PRIVKEY)),
            ]
        return []

    fake_client.on_get_events = on_get_events
    async with test_client.app.app_context():
        identity = await look_up_client_app_identity(
            client_id=CLIENT_ID,
            nostr_client_factory=lambda: fake_client,
        )

    mock_verify_nip05.assert_called_once()

    assert identity is not None
    assert identity.name == "Green Drink"
    assert identity.nip05 is not None
    assert identity.nip05.verification_status == Nip05VerificationStatus.VERIFIED
    assert identity.image_url == "https://greendrink.com/image.png"
    assert identity.allowed_redirect_urls == ["https://greendrink.com/callback"]
    nip68 = identity.app_authority_verification
    assert nip68 is not None
    assert nip68.authority_name == "Important Authority"
    assert nip68.authority_pubkey == Keys.parse(AUTHORITY_PRIVKEY).public_key().to_hex()
    assert nip68.status == Nip68VerificationStatus.VERIFIED


@patch.object(Nip05, "verify", new_callable=AsyncMock)
async def test_kind13195_with_revoked_label(
    mock_verify_nip05: AsyncMock, test_client: QuartClient
) -> None:
    mock_verify_nip05.return_value = Nip05VerificationStatus.VERIFIED
    fake_client = FakeNostrClient()

    id_event = EventBuilder(
        kind=Kind(13195),
        content=json.dumps(
            {
                "name": "Yellow Drink",
                "nip05": "_@yellowdrink.com",
                "image": "https://yellowdrink.com/image.png",
                "allowed_redirect_urls": ["https://yellowdrink.com/callback"],
            }
        ),
        tags=[],
    ).to_event(Keys.parse(CLIENT_PRIVKEY))

    async def on_get_events(filters: List[Filter], source: EventSource):
        filter_kinds = filters[0].as_record().kinds or []
        if Kind(13195) in filter_kinds:
            return [id_event]
        if Kind.from_enum(KindEnum.LABEL()) in filter_kinds:  # pyre-ignore[6]
            return [
                EventBuilder.label("nip68.client_app", ["revoked", "nip68.client_app"])
                .add_tags([Tag.event(id_event.id())])
                .to_event(Keys.parse(AUTHORITY_PRIVKEY)),
                EventBuilder.metadata(
                    Metadata().set_name("Important Authority")
                ).to_event(Keys.parse(AUTHORITY_PRIVKEY)),
            ]
        return []

    fake_client.on_get_events = on_get_events
    async with test_client.app.app_context():
        identity = await look_up_client_app_identity(
            client_id=CLIENT_ID,
            nostr_client_factory=lambda: fake_client,
        )

    mock_verify_nip05.assert_called_once()

    assert identity is not None
    assert identity.name == "Yellow Drink"
    assert identity.nip05 is not None
    assert identity.nip05.verification_status == Nip05VerificationStatus.VERIFIED
    assert identity.image_url == "https://yellowdrink.com/image.png"
    assert identity.allowed_redirect_urls == ["https://yellowdrink.com/callback"]
    nip68 = identity.app_authority_verification
    assert nip68 is not None
    assert nip68.authority_name == "Important Authority"
    assert nip68.authority_pubkey == Keys.parse(AUTHORITY_PRIVKEY).public_key().to_hex()
    assert nip68.status == Nip68VerificationStatus.REVOKED
