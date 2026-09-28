"""
tests/test_national_materials.py

National Material Master tests:

TEST 3: CNMC uniqueness — duplicate identity prevention
TEST 4: Duplicate mapping prevention
TEST 7: Audit record modification attempt → rejected
TEST 8: Transaction rollback (partial approval)
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers, get_token

CANONICAL_ATTRS = {
    "type": "hex bolt",
    "material": "stainless steel",
    "grade": "SS304",
    "diameter": "16mm",
    "length": "50mm",
}


async def create_nm(client: AsyncClient, token: str, **overrides) -> dict:
    payload = {
        "standard_description": "Stainless Steel Hex Bolt M16 x 50mm",
        "category": "Fasteners",
        "canonical_attributes": CANONICAL_ATTRS,
    }
    payload.update(overrides)
    resp = await client.post("/api/national-materials", headers=auth_headers(token), json=payload)
    assert resp.status_code in (201, 409), resp.text
    return resp


# ── TEST 3 — CNMC Uniqueness ──────────────────────────────────────────────────

@pytest.mark.anyio
async def test_cnmc_uniqueness_prevents_duplicate(client: AsyncClient, national_reviewer):
    """
    TEST 3: Create CNMC-000001; attempt same identity again.
    Expected: 409 conflict with existing CNMC returned.
    """
    token = await get_token(client, "NR001", "NRPassword123!")

    # First creation
    r1 = await create_nm(client, token)
    assert r1.status_code == 201
    cnmc1 = r1.json()["cnmc"]
    assert cnmc1.startswith("CNMC-")

    # Second attempt with same identity
    r2 = await create_nm(client, token)
    assert r2.status_code == 409
    err = r2.json()["detail"]["error"]
    assert err["code"] == "DUPLICATE_NATIONAL_MATERIAL"
    # Response must tell caller which existing CNMC holds this identity
    assert "existing_cnmc" in err
    assert err["existing_cnmc"] == cnmc1


@pytest.mark.anyio
async def test_different_attributes_create_different_cnmc(client: AsyncClient, national_reviewer):
    """Different canonical attributes must produce different CNMC."""
    token = await get_token(client, "NR001", "NRPassword123!")

    r1 = await create_nm(
        client, token,
        standard_description="Hex Bolt M10 x 30mm SS316",
        canonical_attributes={"type": "hex bolt", "grade": "SS316", "diameter": "10mm", "length": "30mm"},
    )
    r2 = await create_nm(
        client, token,
        standard_description="Hex Bolt M12 x 40mm SS304",
        canonical_attributes={"type": "hex bolt", "grade": "SS304", "diameter": "12mm", "length": "40mm"},
    )
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["cnmc"] != r2.json()["cnmc"]


@pytest.mark.anyio
async def test_national_material_lifecycle(client: AsyncClient, national_reviewer):
    """Status transitions: DRAFT → ACTIVE → SUSPENDED → DEPRECATED."""
    token = await get_token(client, "NR001", "NRPassword123!")
    r = await create_nm(
        client, token,
        standard_description="Carbon Steel Pipe DN50",
        canonical_attributes={"type": "pipe", "material": "carbon steel", "dn": "50"},
    )
    assert r.status_code == 201
    nm_id = r.json()["id"]
    assert r.json()["status"] == "DRAFT"

    # Activate
    act = await client.post(
        f"/api/national-materials/{nm_id}/activate",
        headers=auth_headers(token),
        json={"reason": "Reviewed and approved."},
    )
    assert act.status_code == 200
    assert act.json()["status"] == "ACTIVE"

    # Suspend
    sus = await client.post(
        f"/api/national-materials/{nm_id}/suspend",
        headers=auth_headers(token),
        json={"reason": "Under re-review."},
    )
    assert sus.status_code == 200
    assert sus.json()["status"] == "SUSPENDED"

    # Deprecate
    dep = await client.post(
        f"/api/national-materials/{nm_id}/deprecate",
        headers=auth_headers(token),
        json={"reason": "Replaced by CNMC-000099."},
    )
    assert dep.status_code == 200
    assert dep.json()["status"] == "DEPRECATED"


# ── TEST 4 — Duplicate Mapping Prevention ────────────────────────────────────

@pytest.mark.anyio
async def test_duplicate_mapping_prevention(client: AsyncClient, national_reviewer):
    """
    TEST 4: Map CNMC-001 → IOCL-123; attempt same mapping again → 409.
    """
    token = await get_token(client, "NR001", "NRPassword123!")

    # Create national material
    nm_resp = await create_nm(
        client, token,
        standard_description="SS304 Gate Valve DN80",
        canonical_attributes={"type": "gate valve", "grade": "SS304", "dn": "80"},
    )
    if nm_resp.status_code == 409:
        nm_id = nm_resp.json()["detail"]["error"]["existing_id"]
    else:
        nm_id = nm_resp.json()["id"]

    mapping_payload = {
        "cpse_id": "IOCL",
        "material_id": "IOCL-MAP-TEST-123",
        "material_code": "IOCL-123",
        "mapping_type": "IDENTICAL",
        "confidence": 0.97,
    }

    # First mapping
    m1 = await client.post(
        f"/api/national-materials/{nm_id}/mappings",
        headers=auth_headers(token),
        json=mapping_payload,
    )
    assert m1.status_code == 201

    # Duplicate attempt
    m2 = await client.post(
        f"/api/national-materials/{nm_id}/mappings",
        headers=auth_headers(token),
        json=mapping_payload,
    )
    assert m2.status_code == 409
    assert m2.json()["detail"]["error"]["code"] == "DUPLICATE_MAPPING"


@pytest.mark.anyio
async def test_multiple_cpse_mappings_to_one_cnmc(client: AsyncClient, national_reviewer):
    """One CNMC can map to multiple CPSEs with different material codes."""
    token = await get_token(client, "NR001", "NRPassword123!")
    nm_resp = await create_nm(
        client, token,
        standard_description="Rubber O-Ring 50mm",
        canonical_attributes={"type": "o-ring", "material": "rubber", "diameter": "50mm"},
    )
    if nm_resp.status_code == 409:
        nm_id = nm_resp.json()["detail"]["error"]["existing_id"]
    else:
        nm_id = nm_resp.json()["id"]

    cpses = [
        {"cpse_id": "IOCL", "material_id": "IOCL-ORING-50", "material_code": "IOCL-500"},
        {"cpse_id": "NTPC", "material_id": "NTPC-ORING-50", "material_code": "NTPC-782"},
        {"cpse_id": "BHEL", "material_id": "BHEL-ORING-50", "material_code": "BHEL-303"},
    ]
    for cpse in cpses:
        resp = await client.post(
            f"/api/national-materials/{nm_id}/mappings",
            headers=auth_headers(token),
            json={**cpse, "mapping_type": "IDENTICAL", "confidence": 0.95},
        )
        assert resp.status_code == 201

    # Verify all 3 mappings exist
    list_resp = await client.get(
        f"/api/national-materials/{nm_id}/mappings", headers=auth_headers(token)
    )
    assert list_resp.status_code == 200
    assert list_resp.json()["pagination"]["total"] >= 3


# ── TEST 7 — Audit Record Protection ─────────────────────────────────────────

@pytest.mark.anyio
async def test_audit_log_is_read_only(client: AsyncClient, national_reviewer):
    """
    TEST 7: Normal users cannot modify or delete audit log entries.
    The API must not expose PUT/DELETE on /api/audit.
    """
    token = await get_token(client, "NR001", "NRPassword123!")

    # Try to PUT to audit endpoint — must 404 or 405
    put_resp = await client.put("/api/audit/1", headers=auth_headers(token), json={"action": "TAMPERED"})
    assert put_resp.status_code in (404, 405)

    # Try to DELETE
    del_resp = await client.delete("/api/audit/1", headers=auth_headers(token))
    assert del_resp.status_code in (404, 405)


@pytest.mark.anyio
async def test_audit_entries_created_on_actions(client: AsyncClient, national_reviewer):
    """Creating a national material must produce an audit log entry."""
    token = await get_token(client, "NR001", "NRPassword123!")

    await create_nm(
        client, token,
        standard_description="Audit Test Valve",
        canonical_attributes={"type": "valve", "material": "bronze", "size": "25mm"},
    )

    audit_resp = await client.get(
        "/api/audit?action=CNMC_CREATED", headers=auth_headers(token)
    )
    assert audit_resp.status_code == 200
    # At least one CNMC_CREATED event exists
    assert audit_resp.json()["pagination"]["total"] >= 1
