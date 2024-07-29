# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved


from typing import Any

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase

from nwc_backend.db import UUID, Column


class ModelBase(DeclarativeBase):
    def __setitem__(self, key: str, value: Any) -> None:
        return setattr(self, key, value)

    id = Column(UUID(), primary_key=True)
    created_at = Column(
        sqlalchemy.DateTime(timezone=True), server_default=sqlalchemy.func.now()
    )
    updated_at = Column(
        sqlalchemy.DateTime(timezone=True),
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    )
