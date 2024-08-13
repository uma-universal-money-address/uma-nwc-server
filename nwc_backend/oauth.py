# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from dataclasses import dataclass
import json
from time import time
from typing import Optional
from uuid import UUID
from nostr_sdk import Keys

from aioauth.models import Token
from quart import Response
from nwc_backend.models.app_connection import AppConnection
from aioauth.utils import generate_token
from werkzeug.datastructures import Headers

from sqlalchemy.orm import Session
from nwc_backend.db import db


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
        client_id: str,
        user_id: UUID,
        nwc_connection_id: UUID,
    ) -> AppConnection:
        with Session(db.engine) as db_session:
            auth_code = generate_auth_code()
            new_key_pair = generate_access_token_pubkey_pair()
            new_access_token = new_key_pair.access_token
            new_nostr_pubkey = new_key_pair.public_key
            new_refresh_token = generate_refresh_token()

            app_connection = AppConnection(
                client_id=client_id,
                user_id=user_id,
                authorization_code=auth_code,
                nwc_connection_id=nwc_connection_id,
                access_token=new_access_token,
                nostr_pubkey=new_nostr_pubkey,
                refresh_token=new_refresh_token,
                access_token_expires_at=int(time()) + ACCESS_TOKEN_EXPIRES_IN,
                refresh_token_expires_at=int(time()) + REFRESH_TOKEN_EXPIRES_IN,
                authorization_code_expires_at=int(time())
                + AUTHORIZATION_CODE_EXPIRES_IN,
            )

            db_session.add(app_connection)
            db_session.commit()

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
        with Session(db.engine) as db_session:
            app_connection: Optional[AppConnection] = (
                db_session.query(AppConnection)
                .filter_by(client_id=client_id, authorization_code=code)
                .first()
            )
            if not app_connection:
                return Response(status=401, response="Invalid authorization code")

            nwc_connection = app_connection.nwc_connection
            response = {
                "access_token": app_connection.access_token,
                "refresh_token": app_connection.refresh_token,
                "expires_in": app_connection.access_token_expires_at - int(time()),
                "token_type": "Bearer",
                # TODO: Add the NWC connection URI
                "nwc_connection_uri": "",
                "commands": nwc_connection.supported_commands,
                "budget": nwc_connection.max_budget_per_month,
                "nwc_expires_at": nwc_connection.connection_expires_at,
            }
            return Response(
                json.dumps(response),
                status=200,
                headers=Headers({"Content-Type": "application/json"}),
            )

    async def get_refresh_token_response(self) -> Response:
        # TODO: Implement this method
        raise NotImplementedError()


authorization_server = OauthAuthorizationServer(OauthStorage())
