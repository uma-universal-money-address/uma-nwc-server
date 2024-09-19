# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from datetime import datetime
from typing import Any
from uuid import UUID

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from nwc_backend.db import UUID as DBUUID
from nwc_backend.db import DateTime


class ModelBase(DeclarativeBase):
    def __setitem__(self, key: str, value: Any) -> None:
        return setattr(self, key, value)

    id: Mapped[UUID] = mapped_column(DBUUID(), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=sqlalchemy.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    )
