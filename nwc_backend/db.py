# pyre-strict

import asyncio
import ssl
import uuid
from datetime import datetime, timezone
from time import monotonic
from typing import Any, Callable, Optional, Type, Union

import sqlalchemy
from botocore.client import BaseClient
from quart import Quart, Response, g
from sqlalchemy import JSON, Uuid, event, types
from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_connection
from sqlalchemy.engine import Dialect, Result
from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.scoping import AsyncSession, async_scoped_session
from sqlalchemy.orm import sessionmaker
from uma_auth.models.currency import Currency


class DateTime(types.TypeDecorator):
    impl = types.TIMESTAMP
    cache_ok = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(timezone=True, *args, **kwargs)  # noqa: B026 FIXME

    @property
    def python_type(self) -> Type[datetime]:
        return datetime

    def process_bind_param(
        self, value: datetime, dialect: Dialect
    ) -> Optional[datetime]:
        if value is None:
            return None

        if value.tzinfo is None:
            raise ValueError("datetime objects must be timezone aware")

        return value.astimezone(timezone.utc)

    def process_result_value(
        self, value: datetime, dialect: Dialect
    ) -> Optional[datetime]:
        if value is None:
            return value

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value


class UUID(Uuid):
    def bind_processor(
        self, dialect: Dialect
    ) -> Optional[Callable[[Optional[uuid.UUID]], Optional[str]]]:
        if dialect.supports_native_uuid and self.native_uuid:
            return None

        def process(value: Optional[uuid.UUID]) -> Optional[str]:
            return str(value) if value is not None else None

        return process


class DBCurrency(types.TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Currency, dialect: Dialect) -> Optional[str]:
        return value.to_json() if value else None

    def process_result_value(self, value: str, dialect: Dialect) -> Optional[Currency]:
        return Currency.from_json(value) if value else None


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


def setup_rds_iam_auth(engine: AsyncEngine) -> None:
    from botocore.session import get_session

    rds: BaseClient = get_session().create_client("rds")
    token_cache: list[Union[float, str]] = []

    @event.listens_for(engine.sync_engine, "do_connect", named=True)
    def provide_token(cparams: dict[str, Any], **_kwargs: Any) -> None:
        if not token_cache or monotonic() - token_cache[0] > 600:  # pyre-ignore[58]
            token = rds.generate_db_auth_token(
                cparams["host"], cparams["port"], cparams["user"]
            )
            token_cache.clear()
            token_cache.extend((monotonic(), token))
        cparams["password"] = token_cache[1]

        # SQLAlchemy converts the URL to connect() arguments, but asyncpg
        # only accepts sslmode et al. in a URL, not as arguments. So we
        # need to construct an SSL context instead.
        if "ssl" not in cparams and engine.url.drivername == "postgresql+asyncpg":
            sslmode = cparams.pop("sslmode", "prefer")
            if sslmode in {"disable", "prefer", "allow", "require"}:
                cparams["ssl"] = sslmode
            else:
                sslctx = ssl.create_default_context(
                    ssl.Purpose.SERVER_AUTH, cafile=cparams.pop("sslrootcert", None)
                )
                sslctx.check_hostname = sslmode == "verify-full"
                cparams["ssl"] = sslctx

    @event.listens_for(engine.sync_engine, "connect", named=True)
    def set_timeout(
        dbapi_connection: AsyncAdapt_asyncpg_connection, **_kwargs: Any
    ) -> None:
        timeout = int(60_000)
        dbapi_connection.await_(
            dbapi_connection._connection.execute(  # noqa: SLF001
                f"SET statement_timeout = {timeout}"
            )
        )
