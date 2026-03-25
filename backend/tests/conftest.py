"""
@module TestConftest
@desc Konfigurasi pytest fixtures untuk testing backend Zonara.
      Menyediakan async client dan test database session.
@author Azhar Maulana
@date 25 Maret 2026
@version 1.0
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import get_db
from app.models.base import Base


# Database URL untuk testing (SQLite in-memory async)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Fixture yang menyediakan database session untuk testing.
    Membuat tabel sebelum test dan menghapus setelah test.

    @return AsyncSession: Test database session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    Fixture yang menyediakan async HTTP client untuk testing endpoint.
    Meng-override dependency get_db agar menggunakan test database.

    @param db_session: Test database session dari fixture.
    @return AsyncClient: HTTP client untuk testing.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
