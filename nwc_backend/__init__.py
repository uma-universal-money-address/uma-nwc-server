# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
import requests
from nostr_sdk import Filter, Kind, KindEnum
from quart import Quart, Response, redirect, request, send_from_directory, session
from sqlalchemy.sql import select
from werkzeug import Response as WerkzeugResponse

import nwc_backend.alembic_importer  # noqa: F401
from nwc_backend.client_app_identity_lookup import look_up_client_app_identity
from nwc_backend.db import UUID, db
from nwc_backend.event_handlers.event_builder import EventBuilder
from nwc_backend.exceptions import (
    ActiveAppConnectionAlreadyExistsException,
    PublishEventFailedException,
)
from nwc_backend.models.app_connection import AppConnection
from nwc_backend.models.app_connection_status import AppConnectionStatus
from nwc_backend.models.client_app import ClientApp
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.spending_limit_frequency import SpendingLimitFrequency
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

    # asyncio.run(init_nostr_client(app))

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
        required_commands = (
            request.args.get("required_commands").split()
            if "required_commands" in request.args
            else []
        )
        optional_commands = request.args.get("optional_commands")
        client_id = request.args.get("client_id")

        vasp_token_payload = jwt.decode(
            short_lived_vasp_token,
            app.config.get("UMA_VASP_JWT_PUBKEY"),
            algorithms=["ES256"],
            # TODO: verify the aud and iss
            options={"verify_aud": False, "verify_iss": False},
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
        user = await User.from_vasp_user_id(vasp_user_id)
        if not user:
            user = User(
                id=uuid4(),
                vasp_user_id=vasp_user_id,
                uma_address=uma_address,
            )
            db.session.add(user)

        # update client app info, or create a new one if it doesn't exist
        client_app_info = await look_up_client_app_identity(client_id)
        if not client_app_info:
            logging.error(
                "Received an empty response for client app identity lookup for client_id %s",
                client_id,
            )
            # TODO: Sync with @brian on how we want to handle this
            return WerkzeugResponse("Client app not found", status=404)

        client_app = await ClientApp.from_client_id(client_id)
        if client_app:
            client_app.app_name = client_app_info.name
            client_app.display_name = client_app_info.display_name
            client_app.verification_status = (
                client_app_info.nip05.verification_status
                if client_app_info.nip05
                else None
            )
            client_app.image_url = client_app_info.image_url
        else:
            client_app = ClientApp(
                client_id=client_id,
                app_name=client_app_info.name,
                display_name=client_app_info.display_name,
                verification_status=(
                    client_app_info.nip05.verification_status
                    if client_app_info.nip05
                    else None
                ),
                image_url=client_app_info.image_url,
            )
            db.session.add(client_app)

        nwc_connection = NWCConnection(
            user_id=user.id,
            client_app_id=client_app.id,
            supported_commands=supported_commands,
        )

        # budget format is <max_amount>.<currency>/<period>
        budget = request.args.get("budget")
        # assert budget is in the correct format
        if budget:
            if len(budget.split(".")) != 2 and len(budget.split("/")) != 2:
                return WerkzeugResponse(
                    "Budget should be in the format <max_amount>.<currency>/<period>",
                    status=400,
                )
            spending_limit_amount = int(budget.split(".")[0])
            spending_limit_currency_code = budget.split(".")[1].split("/")[0]
            period = budget.split("/")[1].lower()

            nwc_connection.spending_limit_amount = spending_limit_amount
            # if currency code is not provided, default to SAT
            nwc_connection.spending_limit_currency_code = (
                spending_limit_currency_code if spending_limit_currency_code else "SAT"
            )
            nwc_connection.spending_limit_frequency = (
                SpendingLimitFrequency(period)
                if period
                else SpendingLimitFrequency.NONE
            )

        # TODO: explore how to deal with expiration of the nwc connection from user input - right now defaulted at 1 year
        connection_expires_at = int(
            (datetime.now(timezone.utc) + timedelta(days=365)).timestamp()
        )
        nwc_connection.connection_expires_at = connection_expires_at

        db.session.add(nwc_connection)
        await db.session.commit()

        # TODO: Verify these are saved on nwc frontend session
        session["short_lived_vasp_token"] = short_lived_vasp_token
        session["nwc_connection_id"] = nwc_connection.id
        session["user_id"] = user.id
        session["client_id"] = request.args.get("client_id")
        session["client_redirect_uri"] = request.args.get("redirect_uri")
        session["client_state"] = request.args.get("state")

        nwc_frontend_new_app = app.config["NWC_APP_ROOT_URL"] + "/apps/new"
        return redirect(nwc_frontend_new_app)

    @app.route("/apps/new", methods=["POST"])
    async def register_new_app_connection() -> WerkzeugResponse:
        uma_vasp_token_exchange_url = app.config["UMA_VASP_TOKEN_EXCHANGE_URL"]
        short_lived_vasp_token = session["short_lived_vasp_token"]
        nwc_connection_id = session["nwc_connection_id"]

        # save the long lived token in the db and create the app connection
        nwc_connection = await db.session.get_one(NWCConnection, nwc_connection_id)

        response = requests.post(
            uma_vasp_token_exchange_url,
            json={
                "token": short_lived_vasp_token,
                "permissions": nwc_connection.supported_commands,
                "expiration": nwc_connection.connection_expires_at,
            },
        )
        response.raise_for_status()
        long_lived_vasp_token = response.json()["token"]

        nwc_connection.long_lived_vasp_token = long_lived_vasp_token
        await db.session.commit()

        oauth_storage = OauthStorage()
        try:
            app_connection = await oauth_storage.create_app_connection(
                nwc_connection_id=nwc_connection_id,
            )
        except ActiveAppConnectionAlreadyExistsException:
            return WerkzeugResponse("Active app connection already exists", status=400)

        # redirect back to the redirect_uri provided by the client app with the auth code and state
        added_parms = {
            "code": app_connection.authorization_code,
            "state": session["client_state"],
        }
        redirect_uri = session["client_redirect_uri"]
        return redirect(
            redirect_uri + "?" + "&".join([f"{k}={v}" for k, v in added_parms.items()])
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

    @app.route("/api/connection/<connectionId>", methods=["GET"])
    async def get_connection(connectionId: str) -> WerkzeugResponse:
        user_id = session.get("user_id")
        if not user_id:
            return WerkzeugResponse("User not authenticated", status=401)
        connection = await db.session.get(AppConnection, UUID(connectionId))
        if not connection:
            return WerkzeugResponse("Connection not found", status=404)
        response = await connection.get_connection_reponse_data()
        return WerkzeugResponse(json.dumps(response), status=200)

    @app.route("/api/connections", methods=["GET"])
    async def get_all_active_connections() -> WerkzeugResponse:
        user_id = session.get("user_id")
        if not user_id:
            return WerkzeugResponse("User not authenticated", status=401)

        result = await db.session.execute(
            select(AppConnection)
            .join(AppConnection.nwc_connection)  # Join with NWCConnection
            .filter(
                NWCConnection.user_id == user_id,
                AppConnection.status == AppConnectionStatus.ACTIVE,
            )
        )
        response = []
        for connection in result.scalars():
            response.append(await connection.get_connection_reponse_data())
        return WerkzeugResponse(json.dumps(response), status=200)

    return app


async def init_nostr_client(app: Quart) -> None:
    await nostr_client.add_relay(NostrConfig.instance(app).relay_url)
    await nostr_client.connect()

    await _publish_nip47_info()

    nip47_filter = (
        Filter()
        .pubkey(NostrConfig.instance(app).identity_keys.public_key())
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
