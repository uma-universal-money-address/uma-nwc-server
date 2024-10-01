from datetime import datetime, timezone

import pytest
from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import (
    create_nwc_connection,
    create_spending_limit,
    jwt_for_user,
)
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.spending_limit import SpendingLimit


@pytest.mark.asyncio
async def test_update_connection_success(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        connection: NWCConnection = await create_nwc_connection()
        token = jwt_for_user(connection.user)

    amount_in_lowest_denom = 7000
    limit_frequency = "monthly"
    expiration = "2029-09-25T01:22:08.388Z"
    status = "Active"
    request_data = {
        "amountInLowestDenom": amount_in_lowest_denom,
        "limitFrequency": limit_frequency,
        "limitEnabled": True,
        "expiration": expiration,
        "status": status,
    }

    response = await test_client.post(
        f"/api/connection/{connection.id}",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    async with test_client.app.app_context():
        updated_connection = await db.session.get(NWCConnection, connection.id)

    assert response.status_code == 200
    assert updated_connection.spending_limit.amount == amount_in_lowest_denom
    assert updated_connection.spending_limit.frequency.value == limit_frequency
    assert updated_connection.connection_expires_at == round(
        datetime.fromisoformat(expiration).timestamp()
    )


@pytest.mark.asyncio
async def test_update_connection_disable_limit_success(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        connection: NWCConnection = await create_nwc_connection()
        spend_limit = await create_spending_limit(nwc_connection=connection)
        token = jwt_for_user(connection.user)

    request_data = {
        "limitEnabled": False,
        "expiration": "2029-09-25T01:22:08.388Z",
        "status": "Active",
    }

    response = await test_client.post(
        f"/api/connection/{connection.id}",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    async with test_client.app.app_context():
        updated_connection = await db.session.get(NWCConnection, connection.id)
        updated_limit = await db.session.get(SpendingLimit, spend_limit.id)

    assert response.status_code == 200
    assert updated_connection.spending_limit is None
    assert updated_limit.end_time < datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_delete_connection_success(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        connection: NWCConnection = await create_nwc_connection()
        token = jwt_for_user(connection.user)

    request_data = {
        "status": "Inactive",
    }

    response = await test_client.post(
        f"/api/connection/{connection.id}",
        json=request_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    async with test_client.app.app_context():
        updated_connection = await db.session.get(NWCConnection, connection.id)

    assert response.status_code == 200
    # when we delete connection we just set the expired time to now, so confirm that
    assert (
        updated_connection.connection_expires_at
        < datetime.now(timezone.utc).timestamp()
    )
