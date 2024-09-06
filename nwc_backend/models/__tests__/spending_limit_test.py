# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timezone
from uuid import uuid4

from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_nwc_connection
from nwc_backend.models.spending_limit import SpendingLimit, SpendingLimitFrequency


async def test_spending_limit(test_client: QuartClient) -> None:
    id = uuid4()
    currency_code = "USD"
    amount = 100
    frequency = SpendingLimitFrequency.MONTHLY
    start_time = datetime.now(timezone.utc)

    async with test_client.app.app_context():
        nwc_connection_id = (await create_nwc_connection()).id
        spending_limit = SpendingLimit(
            id=id,
            nwc_connection_id=nwc_connection_id,
            currency_code=currency_code,
            amount=amount,
            frequency=frequency,
            start_time=start_time,
        )
        db.session.add(spending_limit)
        await db.session.commit()

    async with test_client.app.app_context():
        spending_limit = await db.session.get_one(SpendingLimit, id)
        assert spending_limit.nwc_connection_id == nwc_connection_id
        assert spending_limit.currency_code == currency_code
        assert spending_limit.amount == amount
        assert spending_limit.frequency == frequency
        assert spending_limit.start_time == start_time


async def test_budget_repr(test_client: QuartClient) -> None:
    currency_code = "USD"
    amount = 100
    frequency = SpendingLimitFrequency.MONTHLY
    start_time = datetime.now(timezone.utc)
    budget = f"{amount}.{currency_code}/{frequency.value}"

    async with test_client.app.app_context():
        nwc_connection_id = (await create_nwc_connection()).id
        spending_limit = SpendingLimit.from_budget_repr(
            budget=budget, nwc_connection_id=nwc_connection_id, start_time=start_time
        )
        id = spending_limit.id
        db.session.add(spending_limit)
        await db.session.commit()

    async with test_client.app.app_context():
        spending_limit = await db.session.get_one(SpendingLimit, id)
        assert spending_limit.nwc_connection_id == nwc_connection_id
        assert spending_limit.currency_code == currency_code
        assert spending_limit.amount == amount
        assert spending_limit.frequency == frequency
        assert spending_limit.start_time == start_time
        assert spending_limit.get_budget_repr() == budget
