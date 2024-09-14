# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import select

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase


class SpendingCycleQuote(ModelBase):
    __tablename__ = "spending_cycle_quote"

    nip47_request_id: Mapped[UUID] = mapped_column(
        DBUUID(), ForeignKey("nip47_request.id"), nullable=False
    )
    payment_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    sending_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    sending_currency_amount: Mapped[int] = mapped_column(BigInteger(), nullable=False)

    @staticmethod
    async def from_payment_hash(payment_hash: str) -> Optional["SpendingCycleQuote"]:
        result = await db.session.execute(
            select(SpendingCycleQuote).filter_by(payment_hash=payment_hash).limit(1)
        )
        return result.scalars().first()
