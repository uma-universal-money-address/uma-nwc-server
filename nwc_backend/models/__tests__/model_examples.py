# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timedelta, timezone
from secrets import token_hex
from typing import Optional
from uuid import uuid4

from nostr_sdk import Keys

from nwc_backend.db import db
from nwc_backend.models.app_connection import AppConnection
from nwc_backend.models.app_connection_status import AppConnectionStatus
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.user import User


async def create_user() -> User:
    user = User(id=uuid4(), vasp_user_id=str(uuid4()), uma_address="$alice@uma.me")
    db.session.add(user)
    await db.session.commit()
    return user


async def create_client_app() -> ClientApp:
    nostr_pubkey = Keys.generate().public_key().to_hex()
    identity_relay = "wss://myrelay.info"
    client_app = ClientApp(
        id=uuid4(),
        client_id=f"{nostr_pubkey} {identity_relay}",
        app_name="Blue Drink",
        display_name="Blue Drink",
    )
    db.session.add(client_app)
    await db.session.commit()
    return client_app


async def create_nwc_connection(
    supported_commands: list[Nip47RequestMethod] = [
        Nip47RequestMethod.MAKE_INVOICE,
        Nip47RequestMethod.PAY_INVOICE,
    ],
) -> NWCConnection:
    user = await create_user()
    client_app = await create_client_app()
    nwc_connection = NWCConnection(
        id=uuid4(),
        client_app=client_app,
        user=user,
        supported_commands=[command.value for command in supported_commands],
        long_lived_vasp_token=token_hex(),
        connection_expires_at=int(
            (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
        ),
    )
    db.session.add(nwc_connection)
    await db.session.commit()
    return nwc_connection


async def create_app_connection(
    supported_commands: list[Nip47RequestMethod] = [
        Nip47RequestMethod.MAKE_INVOICE,
        Nip47RequestMethod.PAY_INVOICE,
    ],
    keys: Optional[Keys] = None,
    access_token_expired: bool = False,
) -> AppConnection:
    nwc_connection = await create_nwc_connection(supported_commands)
    keys = keys or Keys.generate()
    now = datetime.now(timezone.utc)
    if access_token_expired:
        access_token_expires_at = now - timedelta(days=30)
    else:
        access_token_expires_at = now + timedelta(days=30)
    app_connection = AppConnection(
        id=uuid4(),
        nwc_connection=nwc_connection,
        nostr_pubkey=keys.public_key().to_hex(),
        access_token=keys.secret_key().to_hex(),
        access_token_expires_at=int(access_token_expires_at.timestamp()),
        refresh_token=token_hex(),
        refresh_token_expires_at=int((now + timedelta(days=120)).timestamp()),
        authorization_code=token_hex(),
        authorization_code_expires_at=int((now + timedelta(minutes=10)).timestamp()),
        status=AppConnectionStatus.ACTIVE,
    )

    db.session.add(app_connection)
    await db.session.commit()
    return app_connection
