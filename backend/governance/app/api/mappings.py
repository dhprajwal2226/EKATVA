"""
app/api/mappings.py

Stand-alone CPSE mapping routes for approve/reject/update/list.
"""
from __future__ import annotations

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import Permission, require_active, require_permission
from app.models.user import User
from app.schemas.mapping import (
    MappingListResponse,
    MappingResponse,
    MappingStatusRequest,
    MappingUpdate,
    PaginationMeta,
)
from app.services import mapping_service

router = APIRouter(prefix="/mappings", tags=["CPSE Material Mappings"])


@router.get("", response_model=MappingListResponse, summary="List all CPSE material mappings")
async def list_mappings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    cpse_id: Optional[str] = Query(None),
    mapping_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    national_material_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MappingListResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_MAPPINGS)
    mappings, total = await mapping_service.list_mappings(
        db, page, limit, national_material_id, cpse_id, mapping_type, status
    )
    pages = math.ceil(total / limit) if total else 0
    return MappingListResponse(
        items=[MappingResponse.model_validate(m) for m in mappings],
        pagination=PaginationMeta(page=page, limit=limit, total=total, pages=pages),
    )


@router.patch("/{mapping_id}", response_model=MappingResponse, summary="Update mapping type or confidence")
async def update_mapping(
    mapping_id: int,
    payload: MappingUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MappingResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_APPROVE_MAPPING)
    mapping = await mapping_service.update_mapping(mapping_id, payload, db, updated_by=current_user, request=request)
    return MappingResponse.model_validate(mapping)


@router.post("/{mapping_id}/approve", response_model=MappingResponse, summary="Approve a PROPOSED mapping")
async def approve_mapping(
    mapping_id: int,
    payload: MappingStatusRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MappingResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_APPROVE_MAPPING)
    mapping = await mapping_service.approve_mapping(mapping_id, db, approved_by=current_user, reason=payload.reason, request=request)
    return MappingResponse.model_validate(mapping)


@router.post("/{mapping_id}/reject", response_model=MappingResponse, summary="Reject a mapping")
async def reject_mapping(
    mapping_id: int,
    payload: MappingStatusRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MappingResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_REJECT_MAPPING)
    mapping = await mapping_service.reject_mapping(mapping_id, db, rejected_by=current_user, reason=payload.reason, request=request)
    return MappingResponse.model_validate(mapping)
