# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os

from quart import Quart, Response, send_from_directory

import nwc_backend.alembic_importer  # noqa: F401
from nwc_backend.api_handlers import (
    client_app_lookup_handler,
    client_app_oauth_handler,
    nwc_connection_handler,
    vasp_token_callback_handler,
)
from nwc_backend.db import db, setup_rds_iam_auth
from nwc_backend.nostr.nostr_client_initializer import init_nostr_client


def create_app() -> Quart:
    app: Quart = Quart(__name__)

    app.config.from_envvar("QUART_CONFIG")
    app.static_folder = app.config["FRONTEND_BUILD_PATH"]
    db.init_app(app)
    if app.config.get("DATABASE_MODE") == "rds":
        setup_rds_iam_auth(db.engine)

    if not app.config.get("QUART_ENV") == "testing":
        app.before_serving(init_nostr_client)

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

    app.add_url_rule(
        "/api/connection/manual",
        view_func=nwc_connection_handler.create_manual_connection,
        methods=["POST"],
    )
    app.add_url_rule(
        "/oauth/auth",
        view_func=client_app_oauth_handler.handle_oauth_request,
        methods=["GET"],
    )
    app.add_url_rule(
        "/apps/new",
        view_func=nwc_connection_handler.create_client_app_connection,
        methods=["POST"],
    )
    app.add_url_rule(
        "/oauth/token",
        view_func=client_app_oauth_handler.handle_token_exchange,
        methods=["POST"],
    )
    app.add_url_rule(
        "/api/connection/<connection_id>",
        view_func=nwc_connection_handler.get_connection,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/connections",
        view_func=nwc_connection_handler.get_all_connections,
        methods=["GET"],
    )
    app.add_url_rule(
        "/auth/vasp_token_callback",
        view_func=vasp_token_callback_handler.handle_vasp_token_callback,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/app",
        view_func=client_app_lookup_handler.get_client_app,
        methods=["GET"],
    )
    app.add_url_rule(
        "/api/connection/<connection_id>/transactions",
        view_func=nwc_connection_handler.get_all_outgoing_payments,
        methods=["GET"],
    )

    return app
