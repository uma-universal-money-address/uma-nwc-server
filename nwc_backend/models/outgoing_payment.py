# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.spending_cycle import SpendingCycle


class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class OutgoingPayment(ModelBase):
    __tablename__ = "outgoing_payment"

    nip47_request_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nip47_request.id"), nullable=False
    )
    quote_id: Mapped[Optional[UUID]] = mapped_column(
        DBUUID(), ForeignKey("payment_quote.id"), nullable=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        DBEnum(PaymentStatus, native_enum=False, nullable=False)
    )
    sending_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    sending_currency_amount: Mapped[int] = mapped_column(BigInteger(), nullable=False)

    # The following fields are only set when spending limit is enabled
    spending_cycle_id: Mapped[Optional[UUID]] = mapped_column(
        DBUUID(), ForeignKey("spending_cycle.id")
    )
    estimated_budget_currency_amount: Mapped[Optional[int]] = mapped_column(
        BigInteger()
    )
    budget_on_hold: Mapped[Optional[int]] = mapped_column(BigInteger())
    settled_budget_currency_amount: Mapped[Optional[int]] = mapped_column(BigInteger())

    spending_cycle: Mapped[Optional[SpendingCycle]] = relationship(
        "SpendingCycle", lazy="joined"
    )
