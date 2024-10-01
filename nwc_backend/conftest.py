# pyre-strict

from typing import AsyncGenerator

from pytest import fixture
from quart.app import QuartClient
from quart.typing import TestClientProtocol

from nwc_backend import create_app
from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase


@fixture()
async def test_client() -> AsyncGenerator[TestClientProtocol, None]:
    app = create_app()
    async with app.test_app() as t_app:
        yield t_app.test_client()


@fixture(autouse=True)
async def run_around_tests(test_client: QuartClient) -> AsyncGenerator[None, None]:
    async with test_client.app.app_context():
        async with db.engine.begin() as conn:
            await conn.run_sync(ModelBase.metadata.create_all)
    yield
