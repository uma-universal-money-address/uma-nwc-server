# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from typing import Any

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase

from nwc_backend.db import UUID, Column


class ModelBase(DeclarativeBase):
    def __setitem__(self, key: str, value: Any) -> None:  # pyre-ignore[2]
        return setattr(self, key, value)

    id: sqlalchemy.Column = Column(UUID(), primary_key=True)
