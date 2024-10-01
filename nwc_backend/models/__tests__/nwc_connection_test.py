from datetime import datetime, timezone
from secrets import token_hex
from time import time
from uuid import uuid4

import pytest
from quart.app import QuartClient
from sqlalchemy.exc import IntegrityError

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import (
    create_client_app,
    create_currency,
    create_user,
)
from nwc_backend.models.nip47_request_method import Nip47RequestMethod
from nwc_backend.models.nwc_connection import NWCConnection
from nwc_backend.models.permissions_grouping import PermissionsGroup
from nwc_backend.models.spending_limit import SpendingLimit, SpendingLimitFrequency


async def test_nwc_connection_model(test_client: QuartClient) -> None:
    id = uuid4()
    async with test_client.app.app_context():
        user_id = (await create_user()).id
        client_app_id = (await create_client_app()).id
        nwc_connection = NWCConnection(
            id=id,
            user_id=user_id,
            client_app_id=client_app_id,
            long_lived_vasp_token=token_hex(),
            connection_expires_at=time(),
            granted_permissions_groups=[
                PermissionsGroup.RECEIVE_PAYMENTS.value,
            ],
            code_challenge=token_hex(),
            redirect_uri="https://example.com",
            budget_currency=create_currency(),
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
            long_lived_vasp_token=token_hex(),
            connection_expires_at=time(),
            spending_limit_id=spending_limit_id,
            code_challenge=token_hex(),
            redirect_uri="https://example.com",
            budget_currency=create_currency(),
        )
        db.session.add(nwc_connection)
        db.session.add(spending_limit)
        await db.session.commit()

    async with test_client.app.app_context():
        nwc_connection = await db.session.get_one(NWCConnection, nwc_connection_id)
        assert nwc_connection.spending_limit.id == spending_limit_id


async def test_client_app_id_or_custom_name_constraint(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        user = await create_user()

    async with test_client.app.app_context():
        client_app_id = (await create_client_app()).id
        nwc_connection = NWCConnection(
            id=uuid4(),
            user_id=user.id,
            client_app_id=client_app_id,
            granted_permissions_groups=[
                PermissionsGroup.RECEIVE_PAYMENTS.value,
            ],
            code_challenge=token_hex(),
            redirect_uri="https://example.com",
            long_lived_vasp_token=token_hex(),
            connection_expires_at=time(),
            budget_currency=create_currency(),
        )
        db.session.add(nwc_connection)
        await db.session.commit()

    async with test_client.app.app_context():
        nwc_connection = NWCConnection(
            id=uuid4(),
            user_id=user.id,
            custom_name="manual connection",
            granted_permissions_groups=[
                PermissionsGroup.RECEIVE_PAYMENTS.value,
            ],
            code_challenge=token_hex(),
            redirect_uri="https://example.com",
            long_lived_vasp_token=token_hex(),
            connection_expires_at=time(),
            budget_currency=create_currency(),
        )
        db.session.add(nwc_connection)
        await db.session.commit()

    async with test_client.app.app_context():
        with pytest.raises(IntegrityError):
            nwc_connection = NWCConnection(
                id=uuid4(),
                user_id=user.id,
                granted_permissions_groups=[
                    PermissionsGroup.RECEIVE_PAYMENTS.value,
                ],
                code_challenge=token_hex(),
                redirect_uri="https://example.com",
                long_lived_vasp_token=token_hex(),
                connection_expires_at=time(),
                budget_currency=create_currency(),
            )
            db.session.add(nwc_connection)
            await db.session.commit()
