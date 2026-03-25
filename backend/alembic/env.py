"""
@module AlembicEnv
@desc Konfigurasi environment Alembic untuk menjalankan migrasi database
      secara asynchronous menggunakan SQLAlchemy AsyncEngine.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import konfigurasi dan seluruh model
from app.config import settings
from app.models import Base  # noqa: F401 — memastikan semua model ter-register

# Alembic Config object
config = context.config

# Override sqlalchemy.url dari environment
config.set_main_option("sqlalchemy.url", settings.database_url)

# Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData target untuk auto-generate migration
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Menjalankan migrasi dalam mode 'offline'.
    Menghasilkan SQL script tanpa koneksi database langsung.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """
    Helper untuk menjalankan migrasi dengan koneksi aktif.

    @param connection: SQLAlchemy Connection object.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Menjalankan migrasi dalam mode 'online' secara asynchronous.
    Membuat AsyncEngine dari konfigurasi Alembic.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Menjalankan migrasi dalam mode 'online'.
    Menggunakan asyncio untuk menjalankan engine asynchronous.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
