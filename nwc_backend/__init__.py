# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os

from quart import (
    Quart,
    send_from_directory,
    redirect,
    url_for,
    request,
    session,
    Response,
)
from werkzeug import Response as WerkzeugResponse

import nwc_backend.alembic_importer  # noqa: F401
from nwc_backend.db import db
from typing import Any


def create_app() -> Quart:

    app: Quart = Quart(__name__)

    app.config.from_envvar("QUART_CONFIG")
    app.static_folder = app.config["FRONTEND_BUILD_PATH"]
    db.init_app(app)

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
