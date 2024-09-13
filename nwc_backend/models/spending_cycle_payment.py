# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from enum import Enum
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.spending_cycle import SpendingCycle


class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class SpendingCyclePayment(ModelBase):
    __tablename__ = "spending_cycle_payment"

    nip47_request_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nip47_request.id"), nullable=False
    )
    spending_cycle_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("spending_cycle.id"), nullable=False
    )
    quote_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("spending_cycle_quote.id"), nullable=True
    )
    estimated_amount: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    budget_on_hold: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        DBEnum(PaymentStatus, native_enum=False, nullable=False)
    )
    settled_amount: Mapped[int] = mapped_column(BigInteger(), nullable=True)

    spending_cycle: Mapped[SpendingCycle] = relationship("SpendingCycle", lazy="joined")
