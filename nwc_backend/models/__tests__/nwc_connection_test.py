# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timezone
from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_client_app, create_user
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.spending_limit import SpendingLimit, SpendingLimitFrequency
from nwc_backend.models.permissions_grouping import PermissionsGroup


async def test_nwc_connection_model(test_client: QuartClient) -> None:
    id = uuid4()
    async with test_client.app.app_context():
        user_id = (await create_user()).id
        client_app_id = (await create_client_app()).id
        nwc_connection = NWCConnection(
            id=id,
            user_id=user_id,
            client_app_id=client_app_id,
            granted_permissions_groups=[
                PermissionsGroup.RECEIVE_PAYMENTS.value,
            ],
        )
        db.session.add(nwc_connection)
        await db.session.commit()

    async with test_client.app.app_context():
        nwc_connection = await db.session.get_one(NWCConnection, id)
        assert nwc_connection.user.id == user_id
        assert nwc_connection.client_app.id == client_app_id
        assert nwc_connection.has_command_permission(Nip47RequestMethod.MAKE_INVOICE)
        assert not nwc_connection.has_command_permission(Nip47RequestMethod.FETCH_QUOTE)
        assert not nwc_connection.spending_limit


async def test_creation_with_spending_limit(
    test_client: QuartClient,
) -> None:
    spending_limit_id = uuid4()
    nwc_connection_id = uuid4()

    async with test_client.app.app_context():
        user_id = (await create_user()).id
        client_app_id = (await create_client_app()).id

        spending_limit = SpendingLimit(
            id=spending_limit_id,
            nwc_connection_id=nwc_connection_id,
            currency_code="USD",
            amount=100,
            frequency=SpendingLimitFrequency.MONTHLY,
            start_time=datetime.now(timezone.utc),
        )
        nwc_connection = NWCConnection(
            id=nwc_connection_id,
            user_id=user_id,
            client_app_id=client_app_id,
            granted_permissions_groups=[
                PermissionsGroup.SEND_PAYMENTS.value,
                PermissionsGroup.RECEIVE_PAYMENTS.value,
            ],
            spending_limit_id=spending_limit_id,
        )
        db.session.add(nwc_connection)
        db.session.add(spending_limit)
        await db.session.commit()

    async with test_client.app.app_context():
        nwc_connection = await db.session.get_one(NWCConnection, nwc_connection_id)
        assert nwc_connection.spending_limit.id == spending_limit_id
