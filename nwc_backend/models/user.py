# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

from nwc_backend.models.model_base import ModelBase
from sqlalchemy import Column, String, Text


class User(ModelBase):
    __tablename__ = "user"

    email: Column[str] = Column(String(255), nullable=False, unique=True)
    access_token: Column[str] = Column(Text)
    refresh_token: Column[str] = Column(Text)
