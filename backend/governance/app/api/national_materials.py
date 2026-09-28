"""
app/api/national_materials.py

National Material Master and CPSE Mapping routes.
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
from app.schemas.mapping import MappingCreate, MappingListResponse, MappingResponse, PaginationMeta as MapPagMeta
from app.schemas.national_material import (
    MappingBriefResponse,
    NationalMaterialCreate,
    NationalMaterialDetailResponse,
    NationalMaterialHistoryItem,
    NationalMaterialListResponse,
    NationalMaterialResponse,
    NationalMaterialUpdate,
    PaginationMeta,
    StatusChangeRequest,
)
from app.services import mapping_service, national_material_service

router = APIRouter(prefix="/national-materials", tags=["National Material Master"])


@router.get("", response_model=NationalMaterialListResponse, summary="Search national material master")
async def list_national_materials(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search in standard description"),
    cnmc: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="DRAFT|PENDING_APPROVAL|ACTIVE|SUSPENDED|DEPRECATED"),
    cpse: Optional[str] = Query(None, description="Filter by mapped CPSE"),
    mapping_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NationalMaterialListResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_NATIONAL_MATERIAL)
    items, total = await national_material_service.list_national_materials(
        db, page, limit, search, cnmc, category, status, cpse, mapping_type
    )
    pages = math.ceil(total / limit) if total else 0
    return NationalMaterialListResponse(
        items=[NationalMaterialResponse.model_validate(i) for i in items],
        pagination=PaginationMeta(page=page, limit=limit, total=total, pages=pages),
    )


@router.get("/{nm_id}", response_model=NationalMaterialDetailResponse, summary="Get national material detail with mappings")
async def get_national_material(
    nm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NationalMaterialDetailResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_NATIONAL_MATERIAL)
    nm = await national_material_service.get_national_material_or_404(nm_id, db)
    resp = NationalMaterialDetailResponse.model_validate(nm)
    resp.mappings = [MappingBriefResponse.model_validate(m) for m in nm.mappings]
    return resp


@router.post("", response_model=NationalMaterialResponse, status_code=201, summary="Create a new national material (DRAFT)")
async def create_national_material(
    payload: NationalMaterialCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NationalMaterialResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_CREATE_CNMC)
    nm = await national_material_service.create_national_material(payload, db, created_by=current_user, request=request)
    return NationalMaterialResponse.model_validate(nm)


@router.patch("/{nm_id}", response_model=NationalMaterialResponse, summary="Update national material attributes")
async def update_national_material(
    nm_id: int,
    payload: NationalMaterialUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NationalMaterialResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_EDIT_NATIONAL_MATERIAL)
    nm = await national_material_service.update_national_material(nm_id, payload, db, updated_by=current_user, request=request)
    return NationalMaterialResponse.model_validate(nm)


@router.post("/{nm_id}/activate", response_model=NationalMaterialResponse, summary="Activate national material (make ACTIVE)")
async def activate_national_material(
    nm_id: int,
    payload: StatusChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NationalMaterialResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_ACTIVATE_NATIONAL_MATERIAL)
    nm = await national_material_service.activate_national_material(nm_id, db, changed_by=current_user, reason=payload.reason, request=request)
    return NationalMaterialResponse.model_validate(nm)


@router.post("/{nm_id}/suspend", response_model=NationalMaterialResponse, summary="Suspend national material")
async def suspend_national_material(
    nm_id: int,
    payload: StatusChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NationalMaterialResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_SUSPEND_NATIONAL_MATERIAL)
    nm = await national_material_service.suspend_national_material(nm_id, db, changed_by=current_user, reason=payload.reason, request=request)
    return NationalMaterialResponse.model_validate(nm)


@router.post("/{nm_id}/deprecate", response_model=NationalMaterialResponse, summary="Deprecate national material")
async def deprecate_national_material(
    nm_id: int,
    payload: StatusChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NationalMaterialResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_DEPRECATE_NATIONAL_MATERIAL)
    nm = await national_material_service.deprecate_national_material(nm_id, db, changed_by=current_user, reason=payload.reason, request=request)
    return NationalMaterialResponse.model_validate(nm)


@router.get("/{nm_id}/mappings", response_model=MappingListResponse, summary="List CPSE mappings for a national material")
async def get_mappings(
    nm_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MappingListResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_MAPPINGS)
    mappings, total = await mapping_service.list_mappings(db, page, limit, national_material_id=nm_id)
    pages = math.ceil(total / limit) if total else 0
    return MappingListResponse(
        items=[MappingResponse.model_validate(m) for m in mappings],
        pagination=MapPagMeta(page=page, limit=limit, total=total, pages=pages),
    )


@router.post("/{nm_id}/mappings", response_model=MappingResponse, status_code=201, summary="Add a CPSE material mapping")
async def create_mapping(
    nm_id: int,
    payload: MappingCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MappingResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_CREATE_MAPPING)
    mapping = await mapping_service.create_mapping(nm_id, payload, db, created_by=current_user, request=request)
    return MappingResponse.model_validate(mapping)


@router.get("/{nm_id}/history", response_model=list[NationalMaterialHistoryItem], summary="Get national material change history")
async def get_history(
    nm_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[NationalMaterialHistoryItem]:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_NATIONAL_MATERIAL)
    history = await national_material_service.get_history(nm_id, db)
    return [NationalMaterialHistoryItem.model_validate(h) for h in history]
