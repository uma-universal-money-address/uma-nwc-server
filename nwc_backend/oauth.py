# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

import json
from dataclasses import dataclass
from time import time
from uuid import UUID, uuid4

from aioauth.models import Token
from aioauth.utils import generate_token
from nostr_sdk import Keys
from quart import Response
from sqlalchemy.exc import IntegrityError
from werkzeug.datastructures import Headers

from nwc_backend.db import db
from nwc_backend.exceptions import ActiveAppConnectionAlreadyExistsException
from nwc_backend.models.app_connection import AppConnection
from nwc_backend.models.app_connection_status import AppConnectionStatus
from nwc_backend.nostr_config import NostrConfig

ACCESS_TOKEN_EXPIRES_IN = 30 * 24 * 60 * 60
REFRESH_TOKEN_EXPIRES_IN = 120 * 24 * 60 * 60
AUTHORIZATION_CODE_EXPIRES_IN = 10 * 60


@dataclass
class NostrKeyPair:
    access_token: str
    public_key: str


def generate_access_token_pubkey_pair() -> NostrKeyPair:
    key = Keys.generate()
    return NostrKeyPair(
        access_token=key.secret_key().to_hex(),
        public_key=key.public_key().to_hex(),
    )


def generate_auth_code() -> str:
    return generate_token()


def generate_refresh_token() -> str:
    return generate_token()


class OauthStorage:
    async def create_app_connection(
        self,
        nwc_connection_id: UUID,
    ) -> AppConnection:
        auth_code = generate_auth_code()
        new_key_pair = generate_access_token_pubkey_pair()
        new_access_token = new_key_pair.access_token
        new_nostr_pubkey = new_key_pair.public_key
        new_refresh_token = generate_refresh_token()

        try:
            app_connection = AppConnection(
                id=uuid4(),
                nwc_connection_id=nwc_connection_id,
                authorization_code=auth_code,
                access_token=new_access_token,
                nostr_pubkey=new_nostr_pubkey,
                refresh_token=new_refresh_token,
                access_token_expires_at=int(time()) + ACCESS_TOKEN_EXPIRES_IN,
                refresh_token_expires_at=int(time()) + REFRESH_TOKEN_EXPIRES_IN,
                authorization_code_expires_at=int(time())
                + AUTHORIZATION_CODE_EXPIRES_IN,
                status=AppConnectionStatus.ACTIVE,
            )
            db.session.add(app_connection)
            await db.session.commit()
        except IntegrityError as e:
            raise ActiveAppConnectionAlreadyExistsException(
                "App connection already exists", e
            )

        return app_connection

    async def refresh_access_token(
        self,
        client_id: str,
        user_id: UUID,
        code: str,
    ) -> Token:
        raise NotImplementedError()


class OauthAuthorizationServer:

    def __init__(self, storage: OauthStorage):
        self.storage = storage

    async def get_exchange_token_response(self, client_id: str, code: str) -> Response:
        app_connection = await AppConnection.from_authorization_code(code)
        if (
            not app_connection
            or app_connection.nwc_connection.client_app.client_id != client_id
        ):
            return Response(status=401, response="Invalid authorization code")

        return self._get_token_response(app_connection)

    async def get_refresh_token_response(
        self, refresh_token: str, client_id: str
    ) -> Response:
        app_connection = await AppConnection.from_refresh_token(refresh_token)
        if (
            not app_connection
            or app_connection.nwc_connection.client_app.client_id != client_id
        ):
            return Response(status=401, response="Invalid refresh token")

        if app_connection.refresh_token_expires_at < int(time()):
            return Response(status=401, response="Refresh token expired")

        if (
            app_connection.nwc_connection.connection_expires_at
            and app_connection.nwc_connection.connection_expires_at < int(time())
        ):
            return Response(status=401, response="Connection expired")

        new_key_pair = generate_access_token_pubkey_pair()
        new_access_token = new_key_pair.access_token
        new_nostr_pubkey = new_key_pair.public_key
        new_refresh_token = generate_refresh_token()

        app_connection.access_token = new_access_token
        app_connection.nostr_pubkey = new_nostr_pubkey
        app_connection.access_token_expires_at = int(time()) + ACCESS_TOKEN_EXPIRES_IN
        app_connection.refresh_token = new_refresh_token
        app_connection.refresh_token_expires_at = int(time()) + REFRESH_TOKEN_EXPIRES_IN
        await db.session.commit()

        return self._get_token_response(app_connection)

    def _get_token_response(self, app_connection: AppConnection) -> Response:
        nwc_connection = app_connection.nwc_connection
        spending_limit = nwc_connection.spending_limit
        nostr_config = NostrConfig.instance()
        wallet_pubkey = nostr_config.identity_keys.public_key().to_hex()
        wallet_relay = nostr_config.relay_url
        response = {
            "access_token": app_connection.access_token,
            "refresh_token": app_connection.refresh_token,
            "expires_in": app_connection.access_token_expires_at - int(time()),
            "token_type": "Bearer",
            # TODO: Add the NWC connection URI
            "nwc_connection_uri": f"nostr+walletconnect://{wallet_pubkey}?relay={wallet_relay}&lud16={nwc_connection.user.uma_address}&secret={app_connection.access_token}",
            "budget": spending_limit.get_budget_repr() if spending_limit else None,
            "commands": nwc_connection.get_all_granted_granular_permissions(),
            "nwc_expires_at": nwc_connection.connection_expires_at,
            "uma_address": nwc_connection.user.uma_address,
        }
        return Response(
            json.dumps(response),
            status=200,
            headers=Headers({"Content-Type": "application/json"}),
        )


authorization_server = OauthAuthorizationServer(OauthStorage())
