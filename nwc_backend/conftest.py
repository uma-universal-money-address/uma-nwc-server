# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from pytest import fixture
from quart.typing import TestClientProtocol

from nwc_backend import create_app
from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase


@fixture()
def test_client() -> TestClientProtocol:
    app = create_app()
    ModelBase.metadata.create_all(db.engine)
    return app.test_app().test_client()
