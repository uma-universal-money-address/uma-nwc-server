# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from time import time
from typing import Any
from urllib.parse import parse_qs, unquote, urlencode, urlparse, urlunparse
from uuid import uuid4

import jwt
import requests
from nostr_sdk import Filter, Kind, KindEnum
from quart import Quart, Response, redirect, request, send_from_directory, session
from quart_cors import route_cors
from sqlalchemy.sql import select
from werkzeug import Response as WerkzeugResponse
from werkzeug.datastructures import MultiDict

import nwc_backend.alembic_importer  # noqa: F401
from nwc_backend.api_handlers import spending_limit_handler
from nwc_backend.api_handlers.vasp_oauth_callback_handler import (
    handle_vasp_oauth_callback,
)
from nwc_backend.client_app_identity_lookup import look_up_client_app_identity
from nwc_backend.db import UUID, db, setup_rds_iam_auth
from nwc_backend.event_handlers.event_builder import EventBuilder
from nwc_backend.exceptions import PublishEventFailedException
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import (
    PERMISSIONS_GROUP_TO_METHODS,
    PermissionsGroup,
)
from nwc_backend.models.spending_limit import SpendingLimit
from nwc_backend.models.spending_limit_frequency import SpendingLimitFrequency
from nwc_backend.nostr_client import nostr_client
from nwc_backend.nostr_config import NostrConfig
from nwc_backend.nostr_notification_handler import NotificationHandler
from nwc_backend.oauth import authorization_server


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
        vasp_token_payload = jwt.decode(
            short_lived_vasp_token,
            app.config.get("UMA_VASP_JWT_PUBKEY"),
            algorithms=["ES256"],
            # TODO: verify the aud and iss
            options={"verify_aud": False, "verify_iss": False},
        )
        uma_address = vasp_token_payload["address"]
        expiry = vasp_token_payload["exp"]

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
        query_params["uma_address"] = uma_address
        query_params["expiry"] = expiry
        query_params["currency"] = request.args.get("currency")
        parsed_url = parsed_url._replace(query=urlencode(query_params, doseq=True))
        frontend_redirect_url = str(urlunparse(parsed_url))

        if not short_lived_vasp_token:
            return WerkzeugResponse("No token provided", status=400)

        return redirect(frontend_redirect_url)

    @app.route("/oauth/auth", methods=["GET"])
    async def oauth_auth() -> WerkzeugResponse:
        short_lived_vasp_token = request.args.get("token")
        if not short_lived_vasp_token:
            uma_vasp_login_url = app.config["UMA_VASP_LOGIN_URL"]
            # redirect back to the same url with the short lived jwt added
            request_params = request.query_string.decode()
            query_params = urlencode(
                {
                    "redirect_uri": app.config["NWC_APP_ROOT_URL"]
                    + "/oauth/auth"
                    + "?"
                    + request_params,
                }
            )
            vasp_url_with_query = uma_vasp_login_url + "?" + query_params
            logging.debug("REDIRECT to %s", vasp_url_with_query)
            return redirect(vasp_url_with_query)

        # if short_lived_jwt is present, means user has logged in and this is redirect  from VASP to frontend, and frontend is making this call
        return await handle_vasp_oauth_callback(app)

    @app.route("/apps/new", methods=["POST"])
    async def register_new_app_connection() -> WerkzeugResponse:
        uma_vasp_token_exchange_url = app.config["UMA_VASP_TOKEN_EXCHANGE_URL"]
        short_lived_vasp_token = session.get("short_lived_vasp_token")
        if not short_lived_vasp_token:
            return WerkzeugResponse("Unauthorized", status=401)
        nwc_connection_id = session["nwc_connection_id"]

        data = await request.get_data()
        data = json.loads(data)
        permissions = data.get("permissions")
        currency_code = data.get("currencyCode")
        amount_in_lowest_denom = data.get("amountInLowestDenom")
        limit_enabled = data.get("limitEnabled")
        limit_frequency = data.get("limitFrequency")
        expiration = data.get("expiration")

        nwc_connection = await db.session.get_one(NWCConnection, nwc_connection_id)

        expires_at = datetime.fromisoformat(expiration)
        nwc_connection.connection_expires_at = expires_at.timestamp()

        if limit_enabled:
            limit_frequency = (
                SpendingLimitFrequency(limit_frequency)
                if limit_frequency
                else SpendingLimitFrequency.NONE
            )
            spending_limit = SpendingLimit(
                id=uuid4(),
                nwc_connection_id=nwc_connection_id,
                currency_code=currency_code or "SAT",
                amount=amount_in_lowest_denom,
                frequency=limit_frequency,
                start_time=datetime.now(timezone.utc),
            )
            db.session.add(spending_limit)
            nwc_connection.spending_limit_id = spending_limit.id
        else:
            nwc_connection.spending_limit_id = None

        # the frontend will always send grouped permissions so we can directly save
        nwc_connection.granted_permissions_groups = permissions
        all_granted_granular_permissions = set()
        for permission in permissions:
            all_granted_granular_permissions.update(
                PERMISSIONS_GROUP_TO_METHODS[PermissionsGroup(permission)]
            )
        all_granted_granular_permissions.update(
            PERMISSIONS_GROUP_TO_METHODS[PermissionsGroup.ALWAYS_GRANTED]
        )

        # save the long lived token in the db and create the app connection
        response = requests.post(
            uma_vasp_token_exchange_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + short_lived_vasp_token,
            },
            json={
                "permissions": list(all_granted_granular_permissions),
                "expiration": nwc_connection.connection_expires_at,
            },
        )
        response.raise_for_status()
        long_lived_vasp_token = response.json()["token"]

        nwc_connection.long_lived_vasp_token = long_lived_vasp_token
        auth_code = nwc_connection.create_oauth_auth_code()
        await db.session.commit()

        return WerkzeugResponse(
            json.dumps(
                {
                    "code": auth_code,
                    "state": session["client_state"],
                }
            )
        )

    @app.route("/oauth/token", methods=["POST"])
    @route_cors(
        allow_origin=["*"],
        allow_methods=["POST"],
        allow_headers=[
            "Authorization",
            "X-User-Agent",
        ],
    )
    async def oauth_exchange() -> Response:
        # Default to post body. Fall back to query params if post body is empty.
        request_data = await request.form
        if not request_data:
            request_data = request.args
        grant_type = request_data.get("grant_type")

        if grant_type == "authorization_code":
            try:
                client_id = _require_string_param(request_data, "client_id")
                code = _require_string_param(request_data, "code")
                redirect_uri = _require_string_param(request_data, "redirect_uri")
                code_verifier = _require_string_param(request_data, "code_verifier")
            except ValueError as e:
                return Response(status=400, response=str(e))
            if not client_id or not code or not redirect_uri or not code_verifier:
                return Response(status=400, response="Missing required parameters")
            response = await authorization_server.get_exchange_token_response(
                client_id=client_id,
                code=code,
                code_verifier=code_verifier,
                redirect_uri=redirect_uri,
            )
            return response
        elif grant_type == "refresh_token":
            refresh_token = request_data.get("refresh_token")
            client_id = request_data.get("client_id")
            return await authorization_server.get_refresh_token_response(
                refresh_token, client_id
            )
        else:
            return Response(status=400, response="Invalid grant type")

    @app.route("/api/connection/<connectionId>", methods=["GET"])
    async def get_connection(connectionId: str) -> WerkzeugResponse:
        user_id = session.get("user_id")
        if not user_id:
            return WerkzeugResponse("User not authenticated", status=401)
        connection = await db.session.get(NWCConnection, UUID(connectionId))
        if not connection:
            return WerkzeugResponse("Connection not found", status=404)
        response = await connection.get_connection_response_data()
        return WerkzeugResponse(json.dumps(response), status=200)

    @app.route("/api/connections", methods=["GET"])
    async def get_all_active_connections() -> WerkzeugResponse:
        user_id = session.get("user_id")
        if not user_id:
            return WerkzeugResponse("User not authenticated", status=401)

        result = await db.session.execute(
            select(NWCConnection).filter(
                NWCConnection.user_id == user_id,
                NWCConnection.connection_expires_at > int(time()),
            )
        )
        response = []
        for connection in result.scalars():
            response.append(await connection.get_connection_response_data())
        return WerkzeugResponse(json.dumps(response), status=200)

    @app.route("/api/app", methods=["GET"])
    async def get_client_app() -> WerkzeugResponse:
        # user_id = session.get("user_id")
        # if not user_id:
        #     return WerkzeugResponse("User not authenticated", status=401)

        client_id = request.args.get("clientId")
        if not client_id:
            return WerkzeugResponse("Client ID not provided", status=400)

        client_app_info = await look_up_client_app_identity(client_id)
        if not client_app_info:
            return WerkzeugResponse("Client app not found", status=404)

        return WerkzeugResponse(
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
        "/api/budget/disable",
        view_func=spending_limit_handler.disable_spending_limit,
        methods=["POST"],
    )

    return app


def _require_string_param(dict: MultiDict, param: str) -> str:
    value = dict.get(param)
    if not value:
        raise ValueError(f"Missing required parameter: {param}")
    if not isinstance(value, str):
        raise ValueError(f"Invalid type for parameter {param}: {type(value)}")
    return value


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
