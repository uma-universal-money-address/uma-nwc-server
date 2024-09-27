# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from uma_auth.models.currency import Currency

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import DateTime, DBCurrency
from nwc_backend.models.model_base import ModelBase


class SpendingCycle(ModelBase):
    __tablename__ = "spending_cycle"

    spending_limit_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("spending_limit.id"), nullable=False
    )
    limit_currency: Mapped[Currency] = mapped_column(DBCurrency(), nullable=False)
    limit_amount: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(),
        nullable=True,
    )
    total_spent: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    total_spent_on_hold: Mapped[int] = mapped_column(BigInteger(), nullable=False)

    def get_available_budget_amount(self) -> int:
        return self.limit_amount - self.total_spent - self.total_spent_on_hold

    def can_make_payment(self, estimate_amount: int) -> bool:
        return (
            self.limit_amount - self.total_spent - self.total_spent_on_hold
            >= estimate_amount
        )

    def has_ended(self) -> bool:
        return self.end_time < datetime.now(timezone.utc) if self.end_time else False


Index(
    "spending_cycle_spending_limit_id_start_time_unique_idx",
    SpendingCycle.spending_limit_id,
    SpendingCycle.start_time,
    unique=True,
)
