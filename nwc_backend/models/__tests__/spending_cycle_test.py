# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import timedelta

import pytest
from quart.app import QuartClient
from sqlalchemy.exc import IntegrityError

from nwc_backend.db import db
from nwc_backend.models.__tests__.model_examples import create_spending_limit
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_limit import SpendingLimitFrequency


async def test_spending_cycle(test_client: QuartClient) -> None:
    async with test_client.app.app_context():
        spending_limit = await create_spending_limit(
            frequency=SpendingLimitFrequency.WEEKLY
        )
        spending_cycle = spending_limit.create_spending_cycle(spending_limit.start_time)
        db.session.add(spending_cycle)
        await db.session.commit()

        spending_cycle = await db.session.get_one(SpendingCycle, spending_cycle.id)
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_amount == spending_limit.amount
        assert spending_cycle.limit_currency == spending_limit.currency.code
        assert spending_cycle.start_time == spending_limit.start_time
        assert spending_cycle.end_time == spending_cycle.start_time + timedelta(days=7)
        assert spending_cycle.total_spent == 0
        assert spending_cycle.total_spent_on_hold == 0
        assert (
            spending_cycle.get_available_budget_amount() == spending_cycle.limit_amount
        )
        assert spending_cycle.can_make_payment(spending_cycle.limit_amount - 10)
        assert spending_cycle.can_make_payment(spending_cycle.limit_amount)
        assert not spending_cycle.can_make_payment(spending_cycle.limit_amount + 10)


async def test_duplicate_spending_limit_creation_throws(
    test_client: QuartClient,
) -> None:
    async with test_client.app.app_context():
        spending_limit = await create_spending_limit(
            frequency=SpendingLimitFrequency.WEEKLY
        )
        spending_cycle = spending_limit.create_spending_cycle(spending_limit.start_time)
        db.session.add(spending_cycle)
        await db.session.commit()

    async with test_client.app.app_context():
        with pytest.raises(IntegrityError):
            spending_cycle = spending_limit.create_spending_cycle(
                spending_limit.start_time
            )
            db.session.add(spending_cycle)
            await db.session.commit()


@pytest.mark.parametrize(
    "delta, is_valid",
    [
        (timedelta(days=7), True),
        (timedelta(days=14), True),
        (timedelta(days=8), False),
        (timedelta(seconds=1), False),
        (timedelta(days=-7), False),
    ],
)
async def test_start_time(
    test_client: QuartClient, delta: timedelta, is_valid: bool
) -> None:
    async with test_client.app.app_context():
        spending_limit = await create_spending_limit(
            frequency=SpendingLimitFrequency.WEEKLY
        )
        if is_valid:
            spending_limit.create_spending_cycle(spending_limit.start_time + delta)
        else:
            with pytest.raises(AssertionError):
                spending_limit.create_spending_cycle(spending_limit.start_time + delta)
