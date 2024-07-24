# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import os
from quart import Quart, send_from_directory
from nwc_backend.db import db
import nwc_backend.alembic_importer  # noqa: F401


def create_app():

    app = Quart(__name__)

    app.config.from_envvar("QUART_CONFIG")
    app.static_folder = app.config["FRONTEND_BUILD_PATH"]
    db.init_app(app)

    @app.route("/hello", defaults={"path": ""})
    async def serve(path):
        return {"hello": "world"}

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    async def serve_frontend(path):
        print("path", path, send_from_directory)
        if path != "" and os.path.exists(app.static_folder + "/" + path):
            return await send_from_directory(app.static_folder, path)
        else:
            return await send_from_directory(app.static_folder, "index.html")

    return app
