# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from nwc_backend.models.Base import Base
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
