# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from enum import Enum
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import Enum as DBEnum
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nwc_backend.db import UUID as DBUUID
from nwc_backend.models.model_base import ModelBase
from nwc_backend.models.receiving_address import ReceivingAddressType
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
    nwc_connection_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nwc_connection.id"), nullable=False
    )
    quote_id: Mapped[Optional[UUID]] = mapped_column(
        DBUUID(), ForeignKey("payment_quote.id"), nullable=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        DBEnum(PaymentStatus, native_enum=False, nullable=False)
    )
    sending_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    sending_currency_amount: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    receiver: Mapped[str] = mapped_column(String(10240), nullable=False)
    receiver_type: Mapped[ReceivingAddressType] = mapped_column(
        DBEnum(ReceivingAddressType, native_enum=False, nullable=False)
    )

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

    __table_args__ = (
        Index(
            "outgoing_payment_connection_id_status_created_at_idx",
            "nwc_connection_id",
            "status",
            "created_at",
        ),
    )

    def to_dict(self) -> dict[str, Any]:
        spending_cycle = self.spending_cycle
        return {
            "id": str(self.id),
            "created_at": str(self.created_at),
            "sending_currency_code": self.sending_currency_code,
            "sending_currency_amount": self.sending_currency_amount,
            "status": self.status.value,
            "receiver": self.receiver,
            "receiver_type": self.receiver_type.name,
            "budget_currency": (
                spending_cycle.limit_currency.to_dict() if spending_cycle else None
            ),
            "budget_currency_amount": self.settled_budget_currency_amount,
            "budget_on_hold": (
                self.budget_on_hold
                if self.budget_on_hold and self.status == PaymentStatus.PENDING
                else None
            ),
        }
