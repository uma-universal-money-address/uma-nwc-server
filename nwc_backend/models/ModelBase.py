# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from sqlalchemy.orm import DeclarativeBase
from nwc_backend.db import Column, UUID


class ModelBase(DeclarativeBase):
    def __setitem__(self, key, value):
        return setattr(self, key, value)

    id = Column(UUID(), primary_key=True)
