# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
import requests
from nostr_sdk import Filter, Kind, KindEnum
from quart import Quart, Response, redirect, request, send_from_directory, session
from sqlalchemy.orm import Session
from werkzeug import Response as WerkzeugResponse

import nwc_backend.alembic_importer  # noqa: F401
from nwc_backend.db import db
from nwc_backend.event_handlers.event_builder import EventBuilder
from nwc_backend.exceptions import PublishEventFailedException
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.user import User
from nwc_backend.nostr_client import nostr_client
from nwc_backend.nostr_config import NostrConfig
from nwc_backend.nostr_notification_handler import NotificationHandler
from nwc_backend.oauth import OauthStorage, authorization_server


def create_app() -> Quart:

    app: Quart = Quart(__name__)

    app.config.from_envvar("QUART_CONFIG")
    app.static_folder = app.config["FRONTEND_BUILD_PATH"]
    db.init_app(app)

    # asyncio.run(init_nostr_client())

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
            return await send_from_directory(static_folder, "index.html")

    @app.route("/oauth/auth", methods=["GET"])
    async def oauth_auth() -> WerkzeugResponse:
        short_lived_vasp_token = request.args.get("token")
        if not short_lived_vasp_token:
            uma_vasp_login_url = app.config["UMA_VASP_LOGIN_URL"]
            # redirect back to the same url with the short lived jwt added
            query_params = {
                "redirect_uri": request.url,
            }
            vasp_url_with_query = (
                uma_vasp_login_url
                + "?"
                + "&".join([f"{k}={v}" for k, v in query_params.items()])
            )
            return redirect(vasp_url_with_query)

        # if short_lived_jwt is present, means user has logged in and this is redirect from the vasp with the full original url
        required_commands = request.args.get("required_commands").split()
        optional_commands = request.args.get("optional_commands")
        budget = request.args.get("budget")
        app_name = request.args.get("app_name")
        description = request.args.get("description")

        vasp_token_payload = jwt.decode(
            short_lived_vasp_token, app.config.get("VASP_NWC_SERVER_SHARED_SECRET")
        )
        vasp_user_id = vasp_token_payload["sub"]
        uma_address = vasp_token_payload["address"]

        # check if all required commands are supported are vasp, and add optional commands supported by vasp
        vasp_supported_commands = app.config.get("VASP_SUPPORTED_COMMANDS")
        for command in required_commands:
            if command not in vasp_supported_commands:
                return WerkzeugResponse(
                    f"Command {command} is not supported by the VASP",
                    status=400,
                )
        supported_commands = required_commands
        if optional_commands:
            optional_commands = optional_commands.split()
            for command in optional_commands:
                if command in vasp_supported_commands:
                    supported_commands.append(command)

        # save the app connection and nwc connection in the db
        with Session(db.engine) as db_session:
            user = db_session.query(User).filter_by(vasp_user_id=vasp_user_id).first()
            if not user:
                user = User(
                    id=uuid4(),
                    vasp_user_id=vasp_user_id,
                    uma_address=uma_address,
                )
                db_session.add(user)

            nwc_connection = NWCConnection(
                id=uuid4(),
                user_id=user.id,
                app_name=app_name,
                description=description,
                max_budget_per_month=budget,
                supported_commands=supported_commands,
            )

            db_session.add(nwc_connection)
            db_session.commit()

        session["short_lived_vasp_token"] = short_lived_vasp_token
        session["nw_connection_id"] = nwc_connection.id
        session["user_id"] = user.id
        session["client_id"] = request.args.get("client_id")
        session["client_redirect_uri"] = request.args.get("redirect_uri")

        nwc_frontend_new_app = app.config["NWC_FRONTEND_NEW_APP_PAGE"]
        return redirect(nwc_frontend_new_app)

    @app.route("/apps/new", methods=["POST"])
    async def register_new_app_connection() -> WerkzeugResponse:
        uma_vasp_token_exchange_url = app.config["UMA_VASP_TOKEN_EXCHANGE_URL"]
        short_lived_vasp_token = session["short_lived_vasp_token"]
        client_id = session["client_id"]
        user_id = session["user_id"]
        nw_connection_id = session["nw_connection_id"]

        # save the long lived token in the db and create the app connection
        with Session(db.engine) as db_session:
            nwc_connection: NWCConnection = db_session.query(NWCConnection).get(
                nw_connection_id
            )

            # exhange the short lived jwt for a long lived jwt
            permissions = nwc_connection.supported_commands
            # TODO: explore how to deal with expiration of the nwc connection from user input - right now defaulted at 1 year
            connection_expires_at = int(
                (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
            )
            response = requests.post(
                uma_vasp_token_exchange_url,
                json={
                    "token": short_lived_vasp_token,
                    "permissions": permissions,
                    "expiration": connection_expires_at,
                },
            )
            response.raise_for_status()
            long_lived_vasp_token = response.json()["token"]

            nwc_connection.long_lived_vasp_token = long_lived_vasp_token
            nwc_connection.connection_expires_at = connection_expires_at
            db_session.commit()

            oauth_storage = OauthStorage()
            app_connection = await oauth_storage.create_app_connection(
                client_id=client_id,
                user_id=user_id,
                nwc_connection_id=nw_connection_id,
            )
            # redirect back to the redirect_uri provided by the client app with the auth code and state
            added_parms = {
                "code": app_connection.authorization_code,
                "state": "success",
            }
            redirect_uri = session["client_redirect_uri"]
            return redirect(
                redirect_uri
                + "?"
                + "&".join([f"{k}={v}" for k, v in added_parms.items()])
            )

    @app.route("/oauth/token", methods=["GET"])
    async def oauth_exchange() -> Response:
        # authenticate the the oauth code for the access token + details
        client_id = request.args.get("client_id")
        grant_type = request.args.get("grant_type")

        if grant_type == "authorization_code":
            code = request.args.get("code")
            response = await authorization_server.get_exchange_token_response(
                client_id=client_id, code=code
            )
            return response
        elif grant_type == "refresh_token":
            return await authorization_server.get_refresh_token_response()
        else:
            return Response(status=400, response="Invalid grant type")

    return app


async def init_nostr_client() -> None:
    await nostr_client.add_relay(NostrConfig.instance().relay_url)
    await nostr_client.connect()

    await _publish_nip47_info()

    nip47_filter = (
        Filter()
        .pubkey(NostrConfig.instance().identity_pubkey)
        .kind(Kind.from_enum(KindEnum.WALLET_CONNECT_REQUEST()))  # pyre-ignore[6]
    )
    await nostr_client.subscribe([nip47_filter])
    await nostr_client.handle_notifications(NotificationHandler())


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
