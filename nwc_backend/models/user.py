# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from nwc_backend.models.model_base import ModelBase


class User(ModelBase):
    __tablename__ = "user"

    vasp_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    uma_address: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    def get_user_id(self):
        return self.id
