# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __setitem__(self, key, value):
        return setattr(self, key, value)
