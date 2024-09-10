# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timedelta, timezone
from secrets import token_hex
from uuid import uuid4

from nostr_sdk import Keys
from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_nwc_connection
from nwc_backend.models.app_connection import AppConnection
from nwc_backend.models.app_connection_status import AppConnectionStatus
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.permissions_grouping import PermissionsGroup


async def test_app_connection_model(test_client: QuartClient) -> None:
    id = uuid4()
    keys = Keys.generate()
    now = datetime.now(timezone.utc)
    granted_permissions_groups = [
        PermissionsGroup.SEND_PAYMENTS,
    ]
    authorization_code = token_hex()
    async with test_client.app.app_context():
        nwc_connection = await create_nwc_connection(granted_permissions_groups)
        client_id = nwc_connection.client_app.client_id
        app_connection = AppConnection(
            id=id,
            nwc_connection_id=nwc_connection.id,
            nostr_pubkey=keys.public_key().to_hex(),
            access_token=keys.secret_key().to_hex(),
            access_token_expires_at=int((now + timedelta(days=30)).timestamp()),
            refresh_token=token_hex(),
            refresh_token_expires_at=int((now + timedelta(days=120)).timestamp()),
            authorization_code=authorization_code,
            authorization_code_expires_at=int(
                (now + timedelta(minutes=10)).timestamp()
            ),
            status=AppConnectionStatus.ACTIVE,
            redirect_uri="https://example.com",
            code_challenge=token_hex(),
            code_challenge_method="S256",
        )
        db.session.add(app_connection)
        await db.session.commit()

    async with test_client.app.app_context():
        app_connection = await AppConnection.from_nostr_pubkey(
            app_connection.nostr_pubkey
        )
        assert isinstance(app_connection, AppConnection)
        assert app_connection.has_command_permission(Nip47RequestMethod.FETCH_QUOTE)
        assert not app_connection.has_command_permission(
            Nip47RequestMethod.MAKE_INVOICE
        )
        assert not app_connection.is_access_token_expired()
        assert not await AppConnection.from_nostr_pubkey(token_hex())

        app_connection = await AppConnection.from_authorization_code(authorization_code)
        assert isinstance(app_connection, AppConnection)
        assert app_connection.nwc_connection.client_app.client_id == client_id
