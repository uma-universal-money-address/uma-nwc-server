# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from quart.app import QuartClient

from nwc_backend.db import db
from nwc_backend.exceptions import InvalidBudgetFormatException
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


async def test_budget_repr_optional_values(test_client: QuartClient) -> None:
    amount = 100
    start_time = datetime.now(timezone.utc)
    budget = f"{amount}"

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
        assert spending_limit.currency_code == "SAT"
        assert spending_limit.amount == amount
        assert spending_limit.frequency == SpendingLimitFrequency.NONE
        assert spending_limit.start_time == start_time


async def test_budget_repr_invalid_format(test_client: QuartClient) -> None:
    amount = 100
    start_time = datetime.now(timezone.utc)

    budget = f"{amount}."
    with pytest.raises(InvalidBudgetFormatException):
        SpendingLimit.from_budget_repr(budget=budget, start_time=start_time)

    budget = f"{amount}.USD/"
    with pytest.raises(InvalidBudgetFormatException):
        SpendingLimit.from_budget_repr(budget=budget, start_time=start_time)

    budget = f"{amount}.Bitcoin/weekly"
    with pytest.raises(InvalidBudgetFormatException):
        SpendingLimit.from_budget_repr(budget=budget, start_time=start_time)


async def test_get_current_spending_cycle(test_client: QuartClient) -> None:
    id = uuid4()
    currency_code = "USD"
    amount = 100
    frequency = SpendingLimitFrequency.WEEKLY
    start_time = datetime.now(timezone.utc) - timedelta(days=9)

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
        spending_cycle = await spending_limit.get_or_create_current_spending_cycle()
        assert spending_cycle.spending_limit_id == spending_limit.id
        assert spending_cycle.limit_currency == currency_code
        assert spending_cycle.limit_amount == amount
        assert spending_cycle.start_time == start_time + timedelta(days=7)
        assert spending_cycle.end_time == start_time + timedelta(days=14)

        # test fetching existing spending cycle
        assert (
            await spending_limit.get_or_create_current_spending_cycle()
        ).id == spending_cycle.id
