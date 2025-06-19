import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add the project root to sys.path
# This is to ensure that alembic can find the app module
# Reason: Alembic runs from the `backend` directory, but models are in `backend/app`
# Adjust if your alembic.ini is not in the `backend` directory relative to project root
project_root = Path(__file__).resolve().parent.parent.parent  # backend/alembic -> backend -> FamilyCart
sys.path.insert(0, str(project_root / "backend"))


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models here to ensure they are registered with Base.metadata
# For example:
# from app.models.user import User
# from app.models.item import Item
# A common pattern is to have an __init__.py in your models directory that imports all models,
# then you can just import that:
import app.models  # This assumes app/models/__init__.py imports all your model classes
from app.core.config import settings  # Import your settings
# Import Base from your models and all models for autogenerate support
from app.db.base import Base  # Adjust if your Base is elsewhere

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url") # Original line
    url = settings.SQLALCHEMY_DATABASE_URI  # Use URI from settings
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Recommended for autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Recommended for autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # section = config.get_section(config.config_ini_section, {}) # Original line
    # section['sqlalchemy.url'] = settings.SQLALCHEMY_DATABASE_URI # Use URI from settings

    # Create a dictionary for async_engine_from_config, ensuring the URL is set correctly
    # The config object itself can be used if sqlalchemy.url is correctly set in alembic.ini
    # or overridden here.

    engine_config = config.get_section(config.config_ini_section, {})
    engine_config["sqlalchemy.url"] = settings.SQLALCHEMY_DATABASE_URI_ASYNC  # Ensure this is your async DB URI

    connectable = async_engine_from_config(
        engine_config,  # Use the modified section or ensure alembic.ini has the async URL
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
