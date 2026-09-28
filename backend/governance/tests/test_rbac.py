"""
tests/test_rbac.py

Role-Based Access Control tests:

TEST 5: CPSE reviewer from IOCL attempts unauthorized NTPC-only action → 403
TEST 6: Viewer attempts approval → 403
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, get_token


@pytest.mark.anyio
async def test_viewer_cannot_approve(client: AsyncClient, viewer_user, national_reviewer, db_session):
    """TEST 6: Viewer must receive 403 when attempting to approve a match."""
    # Create a review as national_reviewer
    nr_token = await get_token(client, "NR001", "NRPassword123!")
    create_resp = await client.post(
        "/api/reviews",
        headers=auth_headers(nr_token),
        json={
            "match_id": "MATCH-VIEWER-TEST",
            "original_ai_classification": "NEAR_DUPLICATE",
            "ai_confidence": 0.85,
            "priority": "NORMAL",
        },
    )
    assert create_resp.status_code == 201
    review_id = create_resp.json()["id"]

    # Viewer tries to approve
    viewer_token = await get_token(client, "VIEW001", "ViewerPass123!")
    resp = await client.post(
        f"/api/reviews/{review_id}/approve",
        headers=auth_headers(viewer_token),
        json={"conflict_acknowledged": False},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"]["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.anyio
async def test_viewer_cannot_create_national_material(client: AsyncClient, viewer_user):
    """Viewer must receive 403 when creating a national material."""
    token = await get_token(client, "VIEW001", "ViewerPass123!")
    resp = await client.post(
        "/api/national-materials",
        headers=auth_headers(token),
        json={
            "standard_description": "Test Valve SS304",
            "canonical_attributes": {"type": "valve"},
        },
    )
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_cpse_reviewer_cannot_approve_match(client: AsyncClient, iocl_reviewer, national_reviewer, db_session):
    """TEST 5 partial: CPSE_REVIEWER does not have CAN_APPROVE_MATCH permission."""
    # Create review
    nr_token = await get_token(client, "NR001", "NRPassword123!")
    create_resp = await client.post(
        "/api/reviews",
        headers=auth_headers(nr_token),
        json={
            "match_id": "MATCH-CPSE-PERM-TEST",
            "original_ai_classification": "IDENTICAL",
            "ai_confidence": 0.99,
        },
    )
    assert create_resp.status_code == 201
    review_id = create_resp.json()["id"]

    iocl_token = await get_token(client, "IOCL001", "IOCLPass123!")
    resp = await client.post(
        f"/api/reviews/{review_id}/approve",
        headers=auth_headers(iocl_token),
        json={"conflict_acknowledged": False},
    )
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_unauthenticated_access_rejected(client: AsyncClient):
    """All protected endpoints must reject requests without a valid JWT."""
    resp = await client.get("/api/reviews")
    assert resp.status_code == 401  # HTTPBearer raises 401 when no credentials


@pytest.mark.anyio
async def test_admin_can_manage_users(client: AsyncClient, admin_user, db_session):
    """ADMIN should be able to create a user."""
    token = await get_token(client, "ADMIN001", "AdminPassword123!")
    resp = await client.post(
        "/api/users",
        headers=auth_headers(token),
        json={
            "employee_id": "NEW001",
            "name": "New Employee",
            "email": "new@test.gov",
            "password": "SecurePass123!",
            "role": "VIEWER",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["employee_id"] == "NEW001"
    assert "password_hash" not in resp.json()


@pytest.mark.anyio
async def test_national_reviewer_cannot_manage_users(client: AsyncClient, national_reviewer):
    """NATIONAL_REVIEWER does not have CAN_MANAGE_USERS."""
    token = await get_token(client, "NR001", "NRPassword123!")
    resp = await client.get("/api/users", headers=auth_headers(token))
    assert resp.status_code == 403
