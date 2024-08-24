# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timedelta, timezone
from secrets import token_hex
from uuid import uuid4

from nostr_sdk import Keys

from nwc_backend.db import db
from nwc_backend.models.app_connection import AppConnection
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.user import User


def create_user() -> User:
    user = User(id=uuid4(), vasp_user_id=str(uuid4()), uma_address="$alice@uma.me")
    db.session.add(user)
    db.session.commit()
    return user


def create_client_app() -> ClientApp:
    nostr_pubkey = Keys.generate().public_key().to_hex()
    identity_relay = "wss://myrelay.info"
    client_app = ClientApp(
        id=uuid4(),
        client_id=f"{nostr_pubkey} {identity_relay}",
        app_name="Blue Drink",
        description="An instant messaging app",
    )
    db.session.add(client_app)
    db.session.commit()
    return client_app


def create_nwc_connection(
    supported_commands: list[Nip47RequestMethod] = [
        Nip47RequestMethod.MAKE_INVOICE,
        Nip47RequestMethod.PAY_INVOICE,
    ],
) -> NWCConnection:
    user = create_user()
    client_app = create_client_app()
    nwc_connection = NWCConnection(
        id=uuid4(),
        user_id=user.id,
        client_app_id=client_app.id,
        supported_commands=[command.value for command in supported_commands],
        long_lived_vasp_token=token_hex(),
        connection_expires_at=int(
            (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
        ),
    )
    db.session.add(nwc_connection)
    db.session.commit()
    return nwc_connection


def create_app_connection(
    supported_commands: list[Nip47RequestMethod] = [
        Nip47RequestMethod.MAKE_INVOICE,
        Nip47RequestMethod.PAY_INVOICE,
    ],
) -> AppConnection:
    nwc_connection = create_nwc_connection(supported_commands)
    keys = Keys.generate()
    now = datetime.now(timezone.utc)
    app_connection = AppConnection(
        id=uuid4(),
        nwc_connection_id=nwc_connection.id,
        nostr_pubkey=keys.public_key().to_hex(),
        access_token=keys.secret_key().to_hex(),
        access_token_expires_at=int((now + timedelta(days=30)).timestamp()),
        refresh_token=token_hex(),
        refresh_token_expires_at=int((now + timedelta(days=120)).timestamp()),
        authorization_code=token_hex(),
        authorization_code_expires_at=int((now + timedelta(minutes=10)).timestamp()),
    )

    db.session.add(app_connection)
    db.session.commit()
    return app_connection
