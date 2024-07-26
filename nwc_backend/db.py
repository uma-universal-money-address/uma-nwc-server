# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import uuid
from typing import Callable, Optional, Type

import sqlalchemy
from quart import Quart
from sqlalchemy import Engine, Uuid, create_engine
from sqlalchemy.engine import Dialect


class UUID(Uuid):
    def bind_processor(
        self, dialect: Dialect
    ) -> Optional[Callable[[Optional[uuid.UUID]], Optional[str]]]:
        if dialect.supports_native_uuid and self.native_uuid:
            return None

        def process(value: Optional[uuid.UUID]) -> Optional[str]:
            return str(value) if value is not None else None

        return process


class SQLAlchemyDB:
    _engine = None

    def __init__(self) -> None:
        setattr(self, "Column", sqlalchemy.Column)  # noqa: B010

    def init_app(self, app: Quart) -> None:
        self._engine = create_engine(app.config["DATABASE_URI"])

    @property
    def engine(self) -> Engine:
        assert self._engine
        return self._engine


db = SQLAlchemyDB()
Column: Type[sqlalchemy.Column] = db.Column