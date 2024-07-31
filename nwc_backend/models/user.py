# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved

from nwc_backend.models.model_base import ModelBase
from sqlalchemy import String
from nwc_backend.db import Column


class User(ModelBase):
    __tablename__ = "user"

    vasp_user_id = Column(String(255), unique=True)
    uma_address = Column(String(255), unique=True)
