# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved


from datetime import datetime, timezone

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import (
    create_nwc_connection,
    create_spending_limit,
    create_user,
)
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.spending_limit import SpendingLimit


async def test_disable_spending_limit__succeeded(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        nwc_connection = await create_nwc_connection()
        spending_limit = await create_spending_limit(nwc_connection=nwc_connection)

    async with test_client.session_transaction() as session:
        session["user_id"] = nwc_connection.user_id

    async with test_client.app.app_context():
        response = await test_client.post(
            "/api/budget/disable", json={"connectionId": str(nwc_connection.id)}
        )
        assert response.status_code == 200

        nwc_connection = await db.session.get_one(NWCConnection, nwc_connection.id)
        assert not nwc_connection.spending_limit
        spending_limit = await db.session.get_one(SpendingLimit, spending_limit.id)
        assert spending_limit.end_time <= datetime.now(timezone.utc)


async def test_disable_spending_limit__not_logged_in(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        nwc_connection = await create_nwc_connection()

    async with test_client.app.app_context():
        response = await test_client.post(
            "/api/budget/disable", json={"connectionId": str(nwc_connection.id)}
        )
        assert response.status_code == 401


async def test_disable_spending_limit__invalid_connection_id(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        user = await create_user()

    async with test_client.session_transaction() as session:
        session["user_id"] = user.id

    async with test_client.app.app_context():
        response = await test_client.post(
            "/api/budget/disable", json={"connectionId": "abc"}
        )
        assert response.status_code == 400


async def test_disable_spending_limit__others_connection(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        nwc_connection = await create_nwc_connection()
        await create_spending_limit(nwc_connection=nwc_connection)

    async with test_client.session_transaction() as session:
        user = await create_user()
        session["user_id"] = user.id

    async with test_client.app.app_context():
        response = await test_client.post(
            "/api/budget/disable", json={"connectionId": str(nwc_connection.id)}
        )
        assert response.status_code == 400


async def test_disable_spending_limit__no_spending_limit(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        nwc_connection = await create_nwc_connection()

    async with test_client.session_transaction() as session:
        session["user_id"] = nwc_connection.user_id

    async with test_client.app.app_context():
        response = await test_client.post(
            "/api/budget/disable", json={"connectionId": str(nwc_connection.id)}
        )
        assert response.status_code == 400
