"""
app/services/mapping_service.py

CPSE material mapping governance.

RULES:
  - The original CPSE material code is NEVER modified.
  - Duplicate (national_material, cpse, material) is prevented at DB level.
  - Mapping approval is audited.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cpse_material_mapping import CPSEMaterialMapping
from app.models.national_material import NationalMaterial
from app.models.user import User
from app.schemas.mapping import MappingCreate, MappingUpdate
from app.services.audit_service import log_action


async def create_mapping(
    national_material_id: int,
    payload: MappingCreate,
    db: AsyncSession,
    created_by: User,
    request: Optional[Request] = None,
) -> CPSEMaterialMapping:
    # Verify national material exists
    nm_result = await db.execute(
        select(NationalMaterial).where(NationalMaterial.id == national_material_id)
    )
    nm = nm_result.scalar_one_or_none()
    if nm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "National material not found."}},
        )

    # Check duplicate
    dup = await db.execute(
        select(CPSEMaterialMapping).where(
            CPSEMaterialMapping.national_material_id == national_material_id,
            CPSEMaterialMapping.cpse_id == payload.cpse_id,
            CPSEMaterialMapping.material_id == payload.material_id,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "DUPLICATE_MAPPING",
                    "message": f"Mapping for CPSE={payload.cpse_id} material={payload.material_id} already exists.",
                }
            },
        )

    mapping = CPSEMaterialMapping(
        national_material_id=national_material_id,
        cpse_id=payload.cpse_id,
        material_id=payload.material_id,
        material_code=payload.material_code,
        mapping_type=payload.mapping_type,
        confidence=payload.confidence,
        source_match_id=payload.source_match_id,
        status="PROPOSED",
    )
    db.add(mapping)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "DUPLICATE_MAPPING", "message": "Duplicate mapping detected."}},
        )

    await log_action(
        db=db, action="MAPPING_CREATED", user_id=created_by.id,
        entity_type="cpse_material_mapping", entity_id=str(mapping.id),
        after_data={
            "national_material_id": national_material_id,
            "cpse_id": payload.cpse_id,
            "material_id": payload.material_id,
            "mapping_type": payload.mapping_type,
        },
        request=request,
    )
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def get_mapping_or_404(mapping_id: int, db: AsyncSession) -> CPSEMaterialMapping:
    result = await db.execute(
        select(CPSEMaterialMapping).where(CPSEMaterialMapping.id == mapping_id)
    )
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Mapping not found."}},
        )
    return mapping


async def approve_mapping(
    mapping_id: int,
    db: AsyncSession,
    approved_by: User,
    reason: Optional[str] = None,
    request: Optional[Request] = None,
) -> CPSEMaterialMapping:
    mapping = await get_mapping_or_404(mapping_id, db)
    if mapping.status not in ("PROPOSED",):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "MAPPING_NOT_APPROVABLE",
                    "message": f"Mapping is in status '{mapping.status}' and cannot be approved.",
                }
            },
        )
    before_status = mapping.status
    mapping.status = "ACTIVE"
    mapping.approved_by_id = approved_by.id
    mapping.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await log_action(
        db=db, action="MAPPING_APPROVED", user_id=approved_by.id,
        entity_type="cpse_material_mapping", entity_id=str(mapping.id),
        before_data={"status": before_status},
        after_data={"status": "ACTIVE"},
        reason=reason, request=request,
    )
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def reject_mapping(
    mapping_id: int,
    db: AsyncSession,
    rejected_by: User,
    reason: Optional[str] = None,
    request: Optional[Request] = None,
) -> CPSEMaterialMapping:
    mapping = await get_mapping_or_404(mapping_id, db)
    before_status = mapping.status
    mapping.status = "REJECTED"
    await db.flush()
    await log_action(
        db=db, action="MAPPING_REJECTED", user_id=rejected_by.id,
        entity_type="cpse_material_mapping", entity_id=str(mapping.id),
        before_data={"status": before_status},
        after_data={"status": "REJECTED"},
        reason=reason, request=request,
    )
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def update_mapping(
    mapping_id: int,
    payload: MappingUpdate,
    db: AsyncSession,
    updated_by: User,
    request: Optional[Request] = None,
) -> CPSEMaterialMapping:
    mapping = await get_mapping_or_404(mapping_id, db)
    before = {"mapping_type": mapping.mapping_type, "confidence": mapping.confidence}
    if payload.mapping_type is not None:
        mapping.mapping_type = payload.mapping_type
    if payload.confidence is not None:
        mapping.confidence = payload.confidence
    await db.flush()
    await log_action(
        db=db, action="MAPPING_UPDATED", user_id=updated_by.id,
        entity_type="cpse_material_mapping", entity_id=str(mapping.id),
        before_data=before,
        after_data={"mapping_type": mapping.mapping_type},
        reason=payload.reason, request=request,
    )
    await db.commit()
    await db.refresh(mapping)
    return mapping


async def list_mappings(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    national_material_id: Optional[int] = None,
    cpse_id: Optional[str] = None,
    mapping_type: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> tuple[list[CPSEMaterialMapping], int]:
    query = select(CPSEMaterialMapping)
    if national_material_id:
        query = query.where(CPSEMaterialMapping.national_material_id == national_material_id)
    if cpse_id:
        query = query.where(CPSEMaterialMapping.cpse_id == cpse_id)
    if mapping_type:
        query = query.where(CPSEMaterialMapping.mapping_type == mapping_type)
    if status_filter:
        query = query.where(CPSEMaterialMapping.status == status_filter)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    offset = (page - 1) * limit
    result = await db.execute(query.offset(offset).limit(limit))
    return list(result.scalars().all()), total
