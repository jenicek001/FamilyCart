import sys
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add the project root to sys.path and load .env
# The root is the 'backend' directory
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
env_path = project_root / ".env"

if env_path.is_file():
    print(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Now that env is loaded, we can import settings and models
# This will now be populated correctly from the loaded .env file
from app.core.config import settings
# Explicitly import all models to ensure they are registered with Base
from app.models.user import User
from app.models.category import Category
from app.models.shopping_list import ShoppingList
from app.models.item import Item
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
    engine_config = config.get_section(config.config_ini_section, {})
    engine_config["sqlalchemy.url"] = settings.SQLALCHEMY_DATABASE_URI_ASYNC

    if not engine_config["sqlalchemy.url"]:
        raise ValueError("Database URL is not set. Check your .env file and configuration.")

    connectable = async_engine_from_config(
        engine_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    import asyncio
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
