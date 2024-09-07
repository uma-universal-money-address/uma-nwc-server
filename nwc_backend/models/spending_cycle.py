# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import DateTime
from nwc_backend.models.model_base import ModelBase


class SpendingCycle(ModelBase):
    __tablename__ = "spending_cycle"

    spending_limit_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("spending_limit.id"), nullable=False
    )
    limit_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    limit_amount: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=True,
    )
    total_spent: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    total_spent_on_hold: Mapped[int] = mapped_column(BigInteger(), nullable=False)


Index(
    "spending_cycle_spending_limit_id_start_time_unique_idx",
    SpendingCycle.spending_limit_id,
    SpendingCycle.start_time,
    unique=True,
)
