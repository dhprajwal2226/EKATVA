"""
app/api/users.py

User management routes. ADMIN-only for write operations.
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
from app.schemas.user import PaginationMeta, UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=UserListResponse, summary="List all users (ADMIN only)")
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    cpse_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserListResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_MANAGE_USERS)
    users, total = await user_service.list_users(db, page, limit, search, role, cpse_id, is_active)
    pages = math.ceil(total / limit) if total else 0
    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        pagination=PaginationMeta(page=page, limit=limit, total=total, pages=pages),
    )


@router.get("/{user_id}", response_model=UserResponse, summary="Get user by ID")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_MANAGE_USERS)
    user = await user_service.get_user_by_id(user_id, db)
    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=201, summary="Create a new user (ADMIN only)")
async def create_user(
    payload: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_MANAGE_USERS)
    user = await user_service.create_user(payload, db, created_by=current_user, request=request)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse, summary="Update user details (ADMIN only)")
async def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_MANAGE_USERS)
    user = await user_service.update_user(user_id, payload, db, updated_by=current_user, request=request)
    return UserResponse.model_validate(user)


@router.post("/{user_id}/activate", response_model=UserResponse, summary="Activate a user (ADMIN only)")
async def activate_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_MANAGE_USERS)
    user = await user_service.set_active(user_id, True, db, changed_by=current_user, request=request)
    return UserResponse.model_validate(user)


@router.post("/{user_id}/deactivate", response_model=UserResponse, summary="Deactivate a user (ADMIN only)")
async def deactivate_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_MANAGE_USERS)
    user = await user_service.set_active(user_id, False, db, changed_by=current_user, request=request)
    return UserResponse.model_validate(user)
