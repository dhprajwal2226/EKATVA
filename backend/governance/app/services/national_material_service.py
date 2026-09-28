"""
app/services/national_material_service.py

National Material Master governance logic.

CNMC generation:
  - Build canonical string from sorted canonical_attributes + standard_description
  - SHA-256 → identity_hash
  - identity_hash uniqueness enforced at DB level (UniqueConstraint)
  - CNMC is sequentially assigned: CNMC-000001, CNMC-000002, …

Governance status flow:
  DRAFT → PENDING_APPROVAL → ACTIVE → SUSPENDED → DEPRECATED

Only ACTIVE records are visible to external consumers (Person 3, Person 4).
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.national_material import NationalMaterial, NationalMaterialHistory
from app.models.user import User
from app.schemas.national_material import NationalMaterialCreate, NationalMaterialUpdate
from app.services.audit_service import log_action


def _build_identity_hash(
    standard_description: str, canonical_attributes: Dict[str, Any]
) -> str:
    """
    Deterministic SHA-256 identity from canonical representation.

    The canonical string is built from sorted attribute keys so that
    attribute insertion order cannot cause false duplicates.
    """
    sorted_attrs = json.dumps(canonical_attributes, sort_keys=True, ensure_ascii=False)
    canonical_str = f"{standard_description.strip().upper()}|{sorted_attrs}"
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


async def _next_cnmc(db: AsyncSession) -> str:
    """Generate the next sequential CNMC code."""
    count = (await db.execute(select(func.count()).select_from(NationalMaterial))).scalar_one()
    return f"CNMC-{(count + 1):06d}"


async def create_national_material(
    payload: NationalMaterialCreate,
    db: AsyncSession,
    created_by: User,
    request: Optional[Request] = None,
) -> NationalMaterial:
    identity_hash = _build_identity_hash(
        payload.standard_description, payload.canonical_attributes
    )

    # Check for existing identity
    existing = await db.execute(
        select(NationalMaterial).where(NationalMaterial.identity_hash == identity_hash)
    )
    existing_nm = existing.scalar_one_or_none()
    if existing_nm:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "DUPLICATE_NATIONAL_MATERIAL",
                    "message": f"A national material with the same identity already exists: {existing_nm.cnmc}",
                    "existing_cnmc": existing_nm.cnmc,
                    "existing_id": existing_nm.id,
                }
            },
        )

    cnmc = await _next_cnmc(db)

    nm = NationalMaterial(
        cnmc=cnmc,
        standard_description=payload.standard_description,
        category=payload.category,
        canonical_attributes=payload.canonical_attributes,
        identity_hash=identity_hash,
        status="DRAFT",
        created_by_id=created_by.id,
    )
    db.add(nm)
    await db.flush()

    # History snapshot
    db.add(NationalMaterialHistory(
        national_material_id=nm.id,
        changed_by_id=created_by.id,
        change_type="CREATED",
        after_data={
            "cnmc": cnmc,
            "standard_description": nm.standard_description,
            "status": nm.status,
            "canonical_attributes": nm.canonical_attributes,
        },
    ))

    await log_action(
        db=db, action="CNMC_CREATED", user_id=created_by.id,
        entity_type="national_material", entity_id=str(nm.id),
        after_data={"cnmc": cnmc, "status": nm.status},
        request=request,
    )
    await db.commit()
    await db.refresh(nm)
    return nm


async def get_national_material_or_404(nm_id: int, db: AsyncSession) -> NationalMaterial:
    result = await db.execute(
        select(NationalMaterial)
        .where(NationalMaterial.id == nm_id)
        .options(selectinload(NationalMaterial.mappings))
    )
    nm = result.scalar_one_or_none()
    if not nm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "National material not found."}},
        )
    return nm


async def update_national_material(
    nm_id: int,
    payload: NationalMaterialUpdate,
    db: AsyncSession,
    updated_by: User,
    request: Optional[Request] = None,
) -> NationalMaterial:
    nm = await get_national_material_or_404(nm_id, db)

    if nm.status == "DEPRECATED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "DEPRECATED_RECORD",
                    "message": "Deprecated national materials cannot be updated.",
                }
            },
        )

    before = {
        "standard_description": nm.standard_description,
        "category": nm.category,
        "canonical_attributes": nm.canonical_attributes,
        "status": nm.status,
    }

    if payload.standard_description is not None:
        nm.standard_description = payload.standard_description
    if payload.category is not None:
        nm.category = payload.category
    if payload.canonical_attributes is not None:
        nm.canonical_attributes = payload.canonical_attributes
        # Recompute identity hash on attribute change
        nm.identity_hash = _build_identity_hash(
            nm.standard_description, nm.canonical_attributes
        )

    await db.flush()
    db.add(NationalMaterialHistory(
        national_material_id=nm.id,
        changed_by_id=updated_by.id,
        change_type="UPDATED",
        before_data=before,
        after_data={
            "standard_description": nm.standard_description,
            "canonical_attributes": nm.canonical_attributes,
        },
        reason=payload.reason,
    ))
    await log_action(
        db=db, action="CNMC_UPDATED", user_id=updated_by.id,
        entity_type="national_material", entity_id=str(nm.id),
        before_data=before,
        after_data={"standard_description": nm.standard_description},
        reason=payload.reason, request=request,
    )
    await db.commit()
    await db.refresh(nm)
    return nm


async def _change_status(
    nm_id: int,
    new_status: str,
    action_code: str,
    allowed_from: list[str],
    db: AsyncSession,
    changed_by: User,
    reason: Optional[str] = None,
    request: Optional[Request] = None,
) -> NationalMaterial:
    nm = await get_national_material_or_404(nm_id, db)

    if nm.status not in allowed_from:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_STATUS_TRANSITION",
                    "message": f"Cannot transition from '{nm.status}' to '{new_status}'.",
                }
            },
        )

    before_status = nm.status
    nm.status = new_status
    if new_status == "ACTIVE":
        nm.approved_by_id = changed_by.id
        nm.approved_at = datetime.now(timezone.utc)

    await db.flush()
    db.add(NationalMaterialHistory(
        national_material_id=nm.id,
        changed_by_id=changed_by.id,
        change_type="STATUS_CHANGED",
        before_data={"status": before_status},
        after_data={"status": new_status},
        reason=reason,
    ))
    await log_action(
        db=db, action=action_code, user_id=changed_by.id,
        entity_type="national_material", entity_id=str(nm.id),
        before_data={"status": before_status},
        after_data={"status": new_status},
        reason=reason, request=request,
    )
    await db.commit()
    await db.refresh(nm)
    return nm


async def activate_national_material(
    nm_id: int, db: AsyncSession, changed_by: User,
    reason: Optional[str] = None, request: Optional[Request] = None,
) -> NationalMaterial:
    return await _change_status(
        nm_id, "ACTIVE", "NATIONAL_MATERIAL_ACTIVATED",
        ["DRAFT", "PENDING_APPROVAL", "SUSPENDED"],
        db, changed_by, reason, request,
    )


async def suspend_national_material(
    nm_id: int, db: AsyncSession, changed_by: User,
    reason: Optional[str] = None, request: Optional[Request] = None,
) -> NationalMaterial:
    return await _change_status(
        nm_id, "SUSPENDED", "NATIONAL_MATERIAL_SUSPENDED",
        ["ACTIVE"],
        db, changed_by, reason, request,
    )


async def deprecate_national_material(
    nm_id: int, db: AsyncSession, changed_by: User,
    reason: Optional[str] = None, request: Optional[Request] = None,
) -> NationalMaterial:
    return await _change_status(
        nm_id, "DEPRECATED", "NATIONAL_MATERIAL_DEPRECATED",
        ["ACTIVE", "SUSPENDED"],
        db, changed_by, reason, request,
    )


async def list_national_materials(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    cnmc: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    cpse: Optional[str] = None,
    mapping_type: Optional[str] = None,
) -> tuple[list[NationalMaterial], int]:
    from app.models.cpse_material_mapping import CPSEMaterialMapping

    query = select(NationalMaterial).options(selectinload(NationalMaterial.mappings))

    if search:
        pattern = f"%{search}%"
        query = query.where(NationalMaterial.standard_description.ilike(pattern))
    if cnmc:
        query = query.where(NationalMaterial.cnmc.ilike(f"%{cnmc}%"))
    if category:
        query = query.where(NationalMaterial.category.ilike(f"%{category}%"))
    if status_filter:
        query = query.where(NationalMaterial.status == status_filter)
    if cpse or mapping_type:
        sub = select(CPSEMaterialMapping.national_material_id)
        if cpse:
            sub = sub.where(CPSEMaterialMapping.cpse_id == cpse)
        if mapping_type:
            sub = sub.where(CPSEMaterialMapping.mapping_type == mapping_type)
        query = query.where(NationalMaterial.id.in_(sub))

    count_q = select(func.count()).select_from(
        select(NationalMaterial.id).filter(
            *(query._where_criteria)
        ).subquery()
    )
    total_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = total_result.scalar_one()

    offset = (page - 1) * limit
    result = await db.execute(
        query.order_by(NationalMaterial.created_at.desc()).offset(offset).limit(limit)
    )
    items = list(result.scalars().all())
    return items, total


async def get_history(nm_id: int, db: AsyncSession) -> list[NationalMaterialHistory]:
    result = await db.execute(
        select(NationalMaterialHistory)
        .where(NationalMaterialHistory.national_material_id == nm_id)
        .order_by(NationalMaterialHistory.timestamp.desc())
    )
    return list(result.scalars().all())
