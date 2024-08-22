# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import AsyncGenerator
from pytest import fixture
from quart.typing import TestClientProtocol

from nwc_backend import create_app
from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase


@fixture()
async def test_client() -> AsyncGenerator[TestClientProtocol, None]:
    app = create_app()
    ModelBase.metadata.create_all(db.engine)
    async with app.test_app() as t_app:
        yield t_app.test_client()
