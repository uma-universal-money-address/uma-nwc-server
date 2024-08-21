# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from uuid import uuid4

from nostr_sdk import Keys
from sqlalchemy.orm import Session

from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.user import User


def create_user(db_session: Session) -> User:
    user = User(id=uuid4(), vasp_user_id=str(uuid4()), uma_address="$alice@uma.me")
    db_session.add(user)
    db_session.commit()
    return user


def create_client_app(db_session: Session) -> ClientApp:
    nostr_pubkey = Keys.generate().public_key().to_hex()
    identity_relay = "wss://myrelay.info"
    client_app = ClientApp(
        id=uuid4(),
        client_id=f"{nostr_pubkey} {identity_relay}",
        app_name="Blue Drink",
        description="An instant messaging app",
    )
    db_session.add(client_app)
    db_session.commit()
    return client_app
