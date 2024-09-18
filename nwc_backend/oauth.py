# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

import json
from time import time

from aioauth.utils import create_s256_code_challenge
from quart import Response
from werkzeug.datastructures import Headers

from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.typing import none_throws


class OauthAuthorizationServer:
    async def get_exchange_token_response(
        self, client_id: str, code: str, code_verifier: str, redirect_uri: str
    ) -> Response:
        nwc_connection = await NWCConnection.from_oauth_authorization_code(code)
        if (
            not nwc_connection
            or not nwc_connection.client_app
            or nwc_connection.client_app.client_id != client_id
        ):
            return Response(status=401, response="Invalid authorization code")

        saved_redirect_uri = nwc_connection.redirect_uri
        saved_code_challenge = nwc_connection.code_challenge
        computed_code_challenge = create_s256_code_challenge(code_verifier)

        if saved_redirect_uri != redirect_uri:
            return Response(status=401, response="Redirect URI mismatch")
        if saved_code_challenge != computed_code_challenge:
            return Response(status=401, response="Code challenge mismatch")

        response = await nwc_connection.refresh_oauth_tokens()
        return Response(
            json.dumps(response),
            status=200,
            headers=Headers({"Content-Type": "application/json"}),
        )

    async def get_refresh_token_response(
        self, refresh_token: str, client_id: str
    ) -> Response:
        nwc_connection = await NWCConnection.from_oauth_refresh_token(refresh_token)
        if (
            not nwc_connection
            or not nwc_connection.client_app
            or nwc_connection.client_app.client_id != client_id
        ):
            return Response(status=401, response="Invalid refresh token")

        if none_throws(nwc_connection.refresh_token_expires_at) < int(time()):
            return Response(status=401, response="Refresh token expired")

        if (
            nwc_connection.connection_expires_at
            and nwc_connection.connection_expires_at < int(time())
        ):
            return Response(status=401, response="Connection expired")

        response = await nwc_connection.refresh_oauth_tokens()
        return Response(
            json.dumps(response),
            status=200,
            headers=Headers({"Content-Type": "application/json"}),
        )


authorization_server = OauthAuthorizationServer()
