"""
app/services/user_service.py

User management business logic.
Only ADMINs can create/manage users.
"""
from __future__ import annotations

import math
from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.audit_service import log_action


async def create_user(
    payload: UserCreate,
    db: AsyncSession,
    created_by: Optional[User] = None,
    request: Optional[Request] = None,
) -> User:
    # Check uniqueness
    existing = await db.execute(
        select(User).where(
            or_(User.employee_id == payload.employee_id, User.email == payload.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "USER_EXISTS",
                    "message": "A user with that employee ID or email already exists.",
                }
            },
        )

    user = User(
        employee_id=payload.employee_id,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=payload.role.value,
        department=payload.department,
        cpse_id=payload.cpse_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    await log_action(
        db=db,
        action="USER_CREATED",
        user_id=created_by.id if created_by else user.id,
        entity_type="user",
        entity_id=str(user.id),
        after_data={
            "employee_id": user.employee_id,
            "role": user.role,
            "email": user.email,
        },
        request=request,
    )
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "User not found."}},
        )
    return user


async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession,
    updated_by: Optional[User] = None,
    request: Optional[Request] = None,
) -> User:
    user = await get_user_by_id(user_id, db)

    before = {
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "cpse_id": user.cpse_id,
    }

    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.role is not None:
        user.role = payload.role.value
    if payload.department is not None:
        user.department = payload.department
    if payload.cpse_id is not None:
        user.cpse_id = payload.cpse_id

    await db.flush()
    await log_action(
        db=db,
        action="USER_UPDATED",
        user_id=updated_by.id if updated_by else None,
        entity_type="user",
        entity_id=str(user.id),
        before_data=before,
        after_data={"name": user.name, "email": user.email, "role": user.role},
        request=request,
    )
    await db.commit()
    await db.refresh(user)
    return user


async def set_active(
    user_id: int,
    is_active: bool,
    db: AsyncSession,
    changed_by: Optional[User] = None,
    request: Optional[Request] = None,
) -> User:
    user = await get_user_by_id(user_id, db)
    before_status = user.is_active
    user.is_active = is_active
    await db.flush()
    action = "USER_ACTIVATED" if is_active else "USER_DEACTIVATED"
    await log_action(
        db=db,
        action=action,
        user_id=changed_by.id if changed_by else None,
        entity_type="user",
        entity_id=str(user.id),
        before_data={"is_active": before_status},
        after_data={"is_active": is_active},
        request=request,
    )
    await db.commit()
    await db.refresh(user)
    return user


async def list_users(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    cpse_id: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> tuple[list[User], int]:
    query = select(User)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                User.name.ilike(pattern),
                User.email.ilike(pattern),
                User.employee_id.ilike(pattern),
            )
        )
    if role:
        query = query.where(User.role == role)
    if cpse_id:
        query = query.where(User.cpse_id == cpse_id)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    offset = (page - 1) * limit
    result = await db.execute(query.offset(offset).limit(limit))
    users = list(result.scalars().all())
    return users, total
