# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import logging
import os
from typing import Any

from nostr_sdk import Filter, Kind, KindEnum
from quart import (
    Quart,
    Response,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)
from werkzeug import Response as WerkzeugResponse

import nwc_backend.alembic_importer  # noqa: F401
from nwc_backend.configs.nostr_config import nostr_config
from nwc_backend.db import db
from nwc_backend.event_handlers.event_builder import EventBuilder
from nwc_backend.event_handlers.nip47_request_method import Nip47RequestMethod
from nwc_backend.exceptions import PublishEventFailedException
from nwc_backend.nostr_client import nostr_client
from nwc_backend.nostr_notification_handler import NotificationHandler


def create_app() -> Quart:

    app: Quart = Quart(__name__)

    app.config.from_envvar("QUART_CONFIG")
    app.static_folder = app.config["FRONTEND_BUILD_PATH"]
    db.init_app(app)

    # asyncio.run(init_nostr_client())

    @app.route("/hello", defaults={"path": ""})
    async def serve(path: str) -> dict[str, Any]:
        return {"hello": "world"}

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    async def serve_frontend(path: str) -> Response:
        print("path", path, send_from_directory)
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
            # redirect back here after login with the short lived jwt
            query_params = {
                "redirect_uri": url_for("/oath/auth"),
            }
            vasp_url_with_query = (
                uma_vasp_login_url
                + "?"
                + "&".join([f"{k}={v}" for k, v in query_params.items()])
            )
            return redirect(vasp_url_with_query)

        # if short_lived_jwt is present, means user has logged in and this is redirect from the vasp
        # save the short lived jwt in the session and redirect to the new app creation page
        session["short_lived_vasp_token"] = short_lived_vasp_token
        nwc_frontend_new_app = app.config["NWC_FRONTEND_NEW_APP_PAGE"]
        return redirect(nwc_frontend_new_app)

    @app.route("/apps/new", methods=["POST"])
    async def register_new_app_connection() -> None:
        # TODO: Implement
        pass

    return app


async def init_nostr_client() -> None:
    await nostr_client.add_relay(nostr_config.relay_url)
    await nostr_client.connect()

    await _publish_nip47_info()

    nip47_filter = (
        Filter()
        .pubkey(nostr_config.identity_pubkey)
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
