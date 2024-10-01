from secrets import token_hex
from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.client_app import ClientApp
from nwc_backend.nostr.client_app_identity_lookup import Nip05VerificationStatus


async def test_client_app_model(test_client: QuartClient) -> None:
    id = uuid4()
    nostr_pubkey = token_hex()
    identity_relay = "wss://myrelay.info"
    client_id = f"{nostr_pubkey} {identity_relay}"
    app_name = "Blue Drink"
    display_name = "Blue Drink"

    async with test_client.app.app_context():
        id = uuid4()
        client_app = ClientApp(
            id=id,
            client_id=client_id,
            app_name=app_name,
            display_name=display_name,
            verification_status=Nip05VerificationStatus.VERIFIED,
        )
        db.session.add(client_app)
        await db.session.commit()

    async with test_client.app.app_context():
        client_app = await db.session.get_one(ClientApp, id)
        assert client_app.client_id == client_id
        assert client_app.app_name == app_name
        assert client_app.display_name == display_name
        assert client_app.verification_status == Nip05VerificationStatus.VERIFIED
        assert client_app.image_url is None
        assert client_app.nostr_pubkey == nostr_pubkey
        assert client_app.identity_relay == identity_relay

        image_url = "https://picsum.photos/200/300"
        # test update
        client_app.image_url = image_url
        await db.session.commit()

    async with test_client.app.app_context():
        client_app = await db.session.get_one(ClientApp, id)
        assert client_app.image_url == image_url
