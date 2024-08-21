# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from secrets import token_hex
from uuid import uuid4

from quart.app import QuartClient
from sqlalchemy.orm import Session

from nwc_backend.db import db
from nwc_backend.models.client_app import ClientApp


async def test_client_app_model(test_client: QuartClient) -> None:
    id = uuid4()
    nostr_pubkey = token_hex()
    identity_relay = "wss://myrelay.info"
    client_id = f"{nostr_pubkey} {identity_relay}"
    app_name = "Blue Drink"
    description = "An instant messaging app"
    # test creation
    with Session(db.engine) as db_session:
        id = uuid4()
        client_app = ClientApp(
            id=id,
            client_id=client_id,
            app_name=app_name,
            description=description,
        )
        db_session.add(client_app)
        db_session.commit()

    with Session(db.engine) as db_session:
        client_app = db_session.query(ClientApp).get(id)
        assert isinstance(client_app, ClientApp)
        assert client_app.client_id == client_id
        assert client_app.app_name == app_name
        assert client_app.description == description
        assert client_app.client_metadata is None
        assert client_app.logo_uri is None
        assert client_app.nostr_pubkey == nostr_pubkey
        assert client_app.identity_relay == identity_relay

        logo_uri = "https://picsum.photos/200/300"
        # test update
        client_app.client_metadata = {"logo_uri": logo_uri}
        db_session.commit()

    with Session(db.engine) as db_session:
        client_app = db_session.query(ClientApp).get(id)
        assert isinstance(client_app, ClientApp)
        assert client_app.logo_uri == logo_uri
