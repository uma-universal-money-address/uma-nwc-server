# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import BigInteger
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import DateTime
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
        return f"{self.amount}.{self.currency_code}/{self.frequency.value}"

    @staticmethod
    def from_budget_repr(
        budget: str,
        start_time: datetime,
        nwc_connection_id: Optional[UUID] = None,
    ) -> "SpendingLimit":
        # budget format is <max_amount>.<currency>/<period>
        if len(budget.split(".")) != 2 and len(budget.split("/")) != 2:
            raise InvalidBudgetFormatException()

        spending_limit_amount = int(budget.split(".")[0])
        spending_limit_currency_code = budget.split(".")[1].split("/")[0]
        period = budget.split("/")[1].lower()

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
        delta = SpendingLimitFrequency.get_time_delta(self.frequency)
        if delta:
            assert (start_time - self.start_time) % delta == timedelta(0)

        return SpendingCycle(
            id=uuid4(),
            spending_limit_id=self.id,
            limit_currency=self.currency_code,
            limit_amount=self.amount,
            start_time=start_time,
            end_time=start_time + delta if delta else None,
            total_spent=0,
            total_spent_on_hold=0,
        )
