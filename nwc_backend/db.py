# Copyright ©, 2022, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import asyncio
import uuid
from time import monotonic
from typing import Any, Callable, Optional, Type, Union

import sqlalchemy
from botocore.client import BaseClient
from quart import Quart, Response, g
from sqlalchemy import Uuid
from sqlalchemy.engine import Dialect, Result
from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.scoping import AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker


class UUID(Uuid):
    def bind_processor(
        self, dialect: Dialect
    ) -> Optional[Callable[[Optional[uuid.UUID]], Optional[str]]]:
        if dialect.supports_native_uuid and self.native_uuid:
            return None

        def process(value: Optional[uuid.UUID]) -> Optional[str]:
            return str(value) if value is not None else None

        return process


class LockingAsyncSession(AsyncSession):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.lock = asyncio.Lock()
        super().__init__(*args, **kwargs)

    async def commit(self, *args: Any, **kwargs: Any) -> None:
        async with self.lock:
            await super().commit(*args, **kwargs)

    async def execute(self, *args: Any, **kwargs: Any) -> Result:
        async with self.lock:
            return await super().execute(*args, **kwargs)

    async def get(self, *args: Any, **kwargs: Any) -> Optional[object]:
        async with self.lock:
            return await super().get(*args, **kwargs)


class AsyncSQLAlchemy:
    _engine = None

    session = async_scoped_session(
        sessionmaker(class_=LockingAsyncSession, future=True, expire_on_commit=False),
        scopefunc=lambda: g._get_current_object(),
    )

    def __init__(self) -> None:
        setattr(self, "Column", sqlalchemy.Column)  # noqa: B010

    def init_app(self, app: Quart) -> None:
        self._engine = create_async_engine(app.config["DATABASE_URI"])
        self.session.session_factory.configure(bind=self._engine)

        @app.teardown_appcontext
        async def shutdown_session(
            response_or_exc: Union[Response, BaseException]
        ) -> Union[Response, BaseException]:
            await db.session.remove()
            return response_or_exc

    @property
    def engine(self) -> AsyncEngine:
        assert self._engine
        return self._engine


db = AsyncSQLAlchemy()
Column: Type[sqlalchemy.Column] = db.Column


def setup_rds_iam_auth(engine: Engine) -> None:
    from botocore.session import get_session

    rds: BaseClient = get_session().create_client("rds")
    token_cache: list[float | str] = []

    @event.listens_for(engine, "do_connect", named=True)
    def provide_token(cparams: dict[str, Any], **_kwargs: Any) -> None:
        if not token_cache or monotonic() - token_cache[0] > 600:  # pyre-ignore[58]
            token = rds.generate_db_auth_token(
                cparams["host"], cparams["port"], cparams["user"]
            )
            token_cache.clear()
            token_cache.extend((monotonic(), token))
        cparams["password"] = token_cache[1]
