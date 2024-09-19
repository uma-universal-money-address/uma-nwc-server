# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import BigInteger
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import select

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import DateTime, db
from nwc_backend.exceptions import InvalidBudgetFormatException
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.spending_cycle import SpendingCycle
from nwc_backend.models.spending_limit_frequency import SpendingLimitFrequency


class SpendingLimit(ModelBase):
    __tablename__ = "spending_limit"

    nwc_connection_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nwc_connection.id"), nullable=False
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    frequency: Mapped[SpendingLimitFrequency] = mapped_column(
        DBEnum(SpendingLimitFrequency, native_enum=False, nullable=False)
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=True,
    )

    def get_budget_repr(self) -> str:
        budget = f"{self.amount}"
        if self.currency_code:
            budget += f".{self.currency_code}"
        if self.frequency:
            budget += f"/{self.frequency.value}"

        return budget

    @staticmethod
    def from_budget_repr(
        budget: str,
        start_time: datetime,
        nwc_connection_id: Optional[UUID] = None,
    ) -> "SpendingLimit":

        # Assert budget string is in the format of "amount.currency_code/period"
        pattern = re.compile(r"^\d+(?:\.\w{3})?(?:/\w+)?$")
        if not pattern.match(budget):
            raise InvalidBudgetFormatException()

        parts = budget.split("/")
        period = parts[1] if len(parts) == 2 else None
        amount_currency = parts[0].split(".")
        spending_limit_amount = int(amount_currency[0])
        spending_limit_currency_code = (
            amount_currency[1] if len(amount_currency) == 2 else None
        )

        return SpendingLimit(
            id=uuid4(),
            nwc_connection_id=nwc_connection_id,
            currency_code=spending_limit_currency_code or "SAT",
            amount=spending_limit_amount,
            frequency=(
                SpendingLimitFrequency(period)
                if period
                else SpendingLimitFrequency.NONE
            ),
            start_time=start_time,
        )

    def create_spending_cycle(self, start_time: datetime) -> SpendingCycle:
        assert start_time >= self.start_time
        cycle_length = SpendingLimitFrequency.get_cycle_length(self.frequency)
        if cycle_length:
            assert (start_time - self.start_time) % cycle_length == timedelta(0)

        return SpendingCycle(
            id=uuid4(),
            spending_limit_id=self.id,
            limit_currency=self.currency_code,
            limit_amount=self.amount,
            start_time=start_time,
            end_time=start_time + cycle_length if cycle_length else None,
            total_spent=0,
            total_spent_on_hold=0,
        )

    async def get_current_cycle_total_remaining(self) -> int:
        current_cycle = await self.get_current_spending_cycle()
        return (
            current_cycle.get_available_budget_amount()
            if current_cycle
            else self.amount
        )

    async def get_current_spending_cycle(self) -> Optional[SpendingCycle]:
        query = (
            select(SpendingCycle)
            .filter(SpendingCycle.spending_limit_id == self.id)
            .order_by(SpendingCycle.start_time.desc())
            .limit(1)
        )
        results = await db.session.execute(query)
        last_spending_cycle = results.scalars().first()
        if last_spending_cycle and not last_spending_cycle.has_ended():
            return last_spending_cycle
        return None

    async def get_or_create_current_spending_cycle(self) -> SpendingCycle:
        current_cycle = await self.get_current_spending_cycle()
        if current_cycle:
            return current_cycle

        current_cycle_start_time = self.get_current_cycle_start_time()
        try:
            spending_cycle = self.create_spending_cycle(current_cycle_start_time)
            db.session.add(spending_cycle)
            await db.session.commit()
            return spending_cycle
        except IntegrityError:
            query = (
                select(SpendingCycle)
                .filter(
                    SpendingCycle.spending_limit_id == self.id,
                    SpendingCycle.start_time == current_cycle_start_time,
                )
                .limit(1)
            )
            results = await db.session.execute(query)
            return results.scalar_one()

    def get_current_cycle_start_time(self) -> datetime:
        cycle_length = SpendingLimitFrequency.get_cycle_length(self.frequency)
        if not cycle_length:
            return self.start_time

        elapsed_time = datetime.now(timezone.utc) - self.start_time
        num_full_cycles = elapsed_time // cycle_length
        return self.start_time + (num_full_cycles * cycle_length)

    def get_current_cycle_end_time(self) -> Optional[datetime]:
        cycle_length = SpendingLimitFrequency.get_cycle_length(self.frequency)
        if not cycle_length:
            return None

        start_time = self.get_current_cycle_start_time()
        return start_time + cycle_length

    async def to_dict(self) -> dict[str, Any]:
        current_cycle = await self.get_current_spending_cycle()
        return {
            "limit_amount": self.amount,
            "limit_frequency": self.frequency.value,
            "amount_used": current_cycle.total_spent if current_cycle else 0,
            "amount_on_hold": (
                current_cycle.total_spent_on_hold if current_cycle else 0
            ),
            # TODO: currency should be fetched from somewhere
            "currency": {
                "code": "USD",
                "name": "US Dollar",
                "symbol": "$",
                "decimals": 2,
                "type": "fiat",
            },
        }
