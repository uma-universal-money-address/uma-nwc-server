import asyncio
from logging.config import fileConfig

from quart import Quart, current_app

from alembic import context
from nwc_backend import create_app
from nwc_backend.db import db
from nwc_backend.models.model_base import ModelBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = ModelBase.metadata


def get_app() -> Quart:
    try:
        return current_app._get_current_object()  # noqa: SLF001 # pyre-ignore[16]
    except RuntimeError:
        return create_app()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_app().config["DATABASE_URI"]

    context.configure(
        url=url,
        target_metadata=target_metadata,
        include_schemas=True,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    get_app().config["DATABASE_STATEMENT_TIMEOUT"] = 0
    async with db.engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """Function to run migrations in a synchronous context."""
    context.configure(
        connection=connection,  # This connection is now a synchronous connection
        target_metadata=target_metadata,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
