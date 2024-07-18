# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from quart import Quart
from nwc_backend.db import db
from nwc_backend.configs.local_dev import DATABASE_URI


def create_app():

    app = Quart(__name__)
    app.config["DATABASE_URI"] = DATABASE_URI
    db.init_app(app)

    @app.route("/")
    async def hello():
        return {"hello": "world"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
