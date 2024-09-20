# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import asyncio
import json
import logging
import os
from time import time
from typing import Any
from urllib.parse import parse_qs, unquote, urlencode, urlparse, urlunparse

from nostr_sdk import Filter, Kind, KindEnum
from quart import Quart, Response, redirect, request, send_from_directory, session
from sqlalchemy.sql import select
from werkzeug import Response as WerkzeugResponse

import nwc_backend.alembic_importer  # noqa: F401
from nwc_backend.api_handlers import (
    client_app_oauth_handler,
    nwc_connection_creation_handler,
)
from nwc_backend.client_app_identity_lookup import look_up_client_app_identity
from nwc_backend.db import db, setup_rds_iam_auth
from nwc_backend.event_handlers.event_builder import EventBuilder
from nwc_backend.exceptions import PublishEventFailedException
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.vasp_jwt import VaspJwt
from nwc_backend.nostr_client import nostr_client
from nwc_backend.nostr_config import NostrConfig
from nwc_backend.nostr_notification_handler import NotificationHandler


def create_app() -> Quart:

    app: Quart = Quart(__name__)

    app.config.from_envvar("QUART_CONFIG")
    app.static_folder = app.config["FRONTEND_BUILD_PATH"]
    db.init_app(app)
    if app.config.get("DATABASE_MODE") == "rds":
        setup_rds_iam_auth(db.engine)

    if not app.config.get("QUART_ENV") == "testing":
        app.before_serving(init_nostr_client)

    @app.route("/hello", defaults={"path": ""})
    async def serve(path: str) -> dict[str, Any]:
        return {"hello": "world"}

    @app.route("/-/alive")
    def alive() -> str:
        return "ok"

    @app.route("/-/ready")
    def ready() -> str:
        return "ok"

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    async def serve_frontend(path: str) -> Response:
        if not app.static_folder:
            return Response("No frontend build path provided", status=500)
        static_folder: str = app.static_folder
        if path != "" and os.path.exists(static_folder + "/" + path):
            return await send_from_directory(static_folder, path)
        else:
            # TODO(LIG-6299): Replace this with a proper template engine.
            with open(static_folder + "/index.html", "r") as file:
                content = file.read()
                content = content.replace(
                    "${{VASP_NAME}}", app.config.get("VASP_NAME") or "UMA NWC"
                )
                content = content.replace(
                    "${{UMA_VASP_LOGIN_URL}}", app.config["UMA_VASP_LOGIN_URL"]
                )
                content = content.replace(
                    "${{VASP_LOGO_URL}}", app.config.get("VASP_LOGO_URL") or "/vasp.svg"
                )
                return Response(content, mimetype="text/html")

    @app.route("/auth/vasp_token_callback", methods=["GET"])
    async def vasp_token_callback() -> WerkzeugResponse:
        short_lived_vasp_token = request.args.get("token")
        if not short_lived_vasp_token:
            return WerkzeugResponse("No token provided", status=400)
        vasp_jwt = VaspJwt.from_jwt(short_lived_vasp_token)

        fe_redirect_path = request.args.get("fe_redirect")
        if fe_redirect_path:
            fe_redirect_path = unquote(fe_redirect_path)
        frontend_redirect_url = app.config["NWC_APP_ROOT_URL"] + (
            fe_redirect_path or "/"
        )
        try:
            parsed_url = urlparse(frontend_redirect_url)
        except ValueError as e:
            return WerkzeugResponse(
                f"Invalid redirect url: {frontend_redirect_url}. {e}", status=400
            )

        query_params = parse_qs(parsed_url.query)
        query_params["token"] = short_lived_vasp_token
        query_params["uma_address"] = [vasp_jwt.uma_address]
        query_params["expiry"] = [vasp_jwt.expiry]
        query_params["currency"] = request.args.get("currency")
        parsed_url = parsed_url._replace(query=urlencode(query_params, doseq=True))
        frontend_redirect_url = str(urlunparse(parsed_url))

        if not short_lived_vasp_token:
            return WerkzeugResponse("No token provided", status=400)

        return redirect(frontend_redirect_url)

    @app.route("/api/connection/<connectionId>", methods=["GET"])
    async def get_connection(connectionId: str) -> Response:
        user_id = session.get("user_id")
        if not user_id:
            return Response("User not authenticated", status=401)
        connection = await db.session.get(NWCConnection, connectionId)
        if not connection or connection.user_id != user_id:
            return Response("Connection not found", status=404)
        response = await connection.to_dict()
        return Response(json.dumps(response), status=200)

    @app.route("/api/connections", methods=["GET"])
    async def get_all_active_connections() -> Response:
        user_id = session.get("user_id")
        if not user_id:
            return Response("User not authenticated", status=401)

        result = await db.session.execute(
            select(NWCConnection).filter(
                NWCConnection.user_id == user_id,
                NWCConnection.connection_expires_at > int(time()),
            )
        )
        response = []
        for connection in result.scalars():
            response.append(await connection.to_dict())
        return Response(json.dumps(response), status=200)

    @app.route("/api/app", methods=["GET"])
    async def get_client_app() -> Response:
        user_id = session.get("user_id")
        if not user_id:
            return Response("User not authenticated", status=401)

        client_id = request.args.get("clientId")
        if not client_id:
            return Response("Client ID not provided", status=400)

        client_app_info = await look_up_client_app_identity(client_id)
        if not client_app_info:
            return Response("Client app not found", status=404)

        return Response(
            json.dumps(
                {
                    "clientId": client_id,
                    "name": client_app_info.display_name,
                    "verified": (
                        client_app_info.nip05.verification_status.value
                        if client_app_info.nip05
                        else None
                    ),
                    "avatar": client_app_info.image_url,
                    "domain": (
                        client_app_info.nip05.domain if client_app_info.nip05 else None
                    ),
                }
            )
        )

    app.add_url_rule(
        "/api/connection/manual",
        view_func=nwc_connection_creation_handler.create_manual_connection,
        methods=["POST"],
    )

    app.add_url_rule(
        "/oauth/auth",
        view_func=client_app_oauth_handler.handle_oauth_request,
        methods=["GET"],
    )

    app.add_url_rule(
        "/apps/new",
        view_func=nwc_connection_creation_handler.create_client_app_connection,
        methods=["POST"],
    )

    app.add_url_rule(
        "/oauth/token",
        view_func=client_app_oauth_handler.handle_token_exchange,
        methods=["POST"],
    )

    return app


async def init_nostr_client() -> None:
    nostr_config = NostrConfig.instance()
    await nostr_client.add_relay(nostr_config.relay_url)
    await nostr_client.connect()

    try:
        await _publish_nip47_info()
    except Exception:
        logging.exception("Failed to publish nip47.")

    nip47_filter = (
        Filter()
        .pubkey(nostr_config.identity_keys.public_key())
        .kind(Kind.from_enum(KindEnum.WALLET_CONNECT_REQUEST()))  # pyre-ignore[6]
    )
    await nostr_client.subscribe([nip47_filter])
    asyncio.create_task(nostr_client.handle_notifications(NotificationHandler()))


async def _publish_nip47_info() -> None:
    nip47_info_event = EventBuilder(
        kind=KindEnum.WALLET_CONNECT_INFO(),  # pyre-ignore[6]
        content=" ".join([method.value for method in list(Nip47RequestMethod)]),
    ).build()
    response = await nostr_client.send_event(nip47_info_event)

    logging.debug(
        "Nip47 info published %s: success %s, failed %s",
        response.id.to_hex(),
        str(response.output.success),
        str(response.output.failed),
    )

    if not response.output.success:
        raise PublishEventFailedException(nip47_info_event, response.output.failed)
