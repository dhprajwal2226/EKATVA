"""
tests/test_auth.py

Authentication tests:
  - Successful login returns tokens
  - Invalid password returns generic 401 (no account enumeration)
  - Inactive account returns 403
  - /me returns correct profile
  - Token refresh works
"""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.conftest import admin_user, auth_headers, get_token


@pytest.mark.anyio
async def test_login_success(client: AsyncClient, admin_user):
    resp = await client.post(
        "/api/auth/login",
        json={"login": "ADMIN001", "password": "AdminPassword123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient, admin_user):
    resp = await client.post(
        "/api/auth/login",
        json={"login": "ADMIN001", "password": "WRONG_PASSWORD"},
    )
    assert resp.status_code == 401
    # Generic message — must not reveal "email exists" or "password wrong"
    msg = resp.json()["detail"]["error"]["message"]
    assert "Invalid credentials" in msg


@pytest.mark.anyio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post(
        "/api/auth/login",
        json={"login": "ghost@nobody.com", "password": "anything123!"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_login_inactive_user(client: AsyncClient, db_session, admin_user):
    # Deactivate the admin
    admin_user.is_active = False
    db_session.add(admin_user)
    await db_session.commit()

    resp = await client.post(
        "/api/auth/login",
        json={"login": "ADMIN001", "password": "AdminPassword123!"},
    )
    assert resp.status_code == 403

    # Restore
    admin_user.is_active = True
    db_session.add(admin_user)
    await db_session.commit()


@pytest.mark.anyio
async def test_me_endpoint(client: AsyncClient, admin_user):
    token = await get_token(client, "ADMIN001", "AdminPassword123!")
    resp = await client.get("/api/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == "ADMIN001"
    assert data["role"] == "ADMIN"
    assert "password_hash" not in data  # NEVER return hash


@pytest.mark.anyio
async def test_token_refresh(client: AsyncClient, admin_user):
    login_resp = await client.post(
        "/api/auth/login",
        json={"login": "ADMIN001", "password": "AdminPassword123!"},
    )
    refresh_token = login_resp.json()["refresh_token"]
    resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.anyio
async def test_invalid_token_rejected(client: AsyncClient):
    resp = await client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401
