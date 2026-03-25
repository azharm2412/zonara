"""
@module Database
@desc Konfigurasi koneksi database asynchronous menggunakan SQLAlchemy + asyncpg.
      Menyediakan engine, session factory, dan dependency injection untuk FastAPI.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import logging
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Async Engine — Connection Pool ke PostgreSQL
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=5,
    max_overflow=3,
    pool_pre_ping=True,
)

# ---------------------------------------------------------------------------
# Session Factory — Menghasilkan AsyncSession untuk setiap request
# ---------------------------------------------------------------------------
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency injection untuk FastAPI.
    Menghasilkan satu AsyncSession per request dan memastikan
    session ditutup setelah request selesai.

    @return AsyncSession: Sesi database asynchronous.
    @raises Exception: Jika koneksi database gagal.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as exc:
            logger.error("Database session error: %s", str(exc))
            await session.rollback()
            raise
        finally:
            await session.close()
