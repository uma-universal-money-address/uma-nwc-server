# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import select

from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase


class User(ModelBase):
    __tablename__ = "user"

    vasp_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    uma_address: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    @staticmethod
    async def from_vasp_user_id(
        vasp_user_id: str,
    ) -> Optional["User"]:
        result = await db.session.execute(
            select(User).filter_by(vasp_user_id=vasp_user_id).limit(1)
        )
        return result.scalars().first()
