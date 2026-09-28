"""
tests/conftest.py

Pytest fixtures for the governance test suite.
Uses an in-memory SQLite database (via aiosqlite) for fast isolated tests.
All fixtures are async-compatible via anyio.
"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.user import User

# Use in-memory SQLite for tests — no real Postgres required
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Per-test DB session that recreates tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client with DB session override."""
    async def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ── User fixtures ─────────────────────────────────────────────────────────────

async def _make_user(db: AsyncSession, **kwargs) -> User:
    user = User(**kwargs)
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session) -> User:
    return await _make_user(
        db_session,
        employee_id="ADMIN001",
        name="Admin User",
        email="admin@test.gov",
        password_hash=hash_password("AdminPassword123!"),
        role="ADMIN",
        department="Central",
        cpse_id=None,
        is_active=True,
    )


@pytest_asyncio.fixture
async def national_reviewer(db_session) -> User:
    return await _make_user(
        db_session,
        employee_id="NR001",
        name="National Reviewer",
        email="nr@test.gov",
        password_hash=hash_password("NRPassword123!"),
        role="NATIONAL_REVIEWER",
        department="National",
        cpse_id=None,
        is_active=True,
    )


@pytest_asyncio.fixture
async def iocl_reviewer(db_session) -> User:
    return await _make_user(
        db_session,
        employee_id="IOCL001",
        name="IOCL Reviewer",
        email="reviewer@iocl.gov",
        password_hash=hash_password("IOCLPass123!"),
        role="CPSE_REVIEWER",
        department="IOCL Procurement",
        cpse_id="IOCL",
        is_active=True,
    )


@pytest_asyncio.fixture
async def viewer_user(db_session) -> User:
    return await _make_user(
        db_session,
        employee_id="VIEW001",
        name="Viewer User",
        email="viewer@test.gov",
        password_hash=hash_password("ViewerPass123!"),
        role="VIEWER",
        department="Finance",
        cpse_id=None,
        is_active=True,
    )


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def get_token(client: AsyncClient, login: str, password: str) -> str:
    resp = await client.post("/api/auth/login", json={"login": login, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]
