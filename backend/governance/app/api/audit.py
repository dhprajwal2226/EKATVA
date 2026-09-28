"""
app/api/audit.py

Read-only audit log routes.
Only INVESTIGATOR, NATIONAL_REVIEWER, and ADMIN can view audit logs.
Normal users cannot UPDATE or DELETE audit entries.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import Permission, require_active, require_permission
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditListResponse, AuditLogResponse, PaginationMeta

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("", response_model=AuditListResponse, summary="Query audit trail")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None, description="Filter by action code"),
    user_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    from_ts: Optional[datetime] = Query(None, description="ISO8601 start timestamp"),
    to_ts: Optional[datetime] = Query(None, description="ISO8601 end timestamp"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AuditListResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_AUDIT)

    from sqlalchemy import func

    query = select(AuditLog)
    if action:
        query = query.where(AuditLog.action == action)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    if from_ts:
        query = query.where(AuditLog.timestamp >= from_ts)
    if to_ts:
        query = query.where(AuditLog.timestamp <= to_ts)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    offset = (page - 1) * limit
    result = await db.execute(query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit))
    logs = list(result.scalars().all())
    pages = math.ceil(total / limit) if total else 0
    return AuditListResponse(
        items=[AuditLogResponse.model_validate(l) for l in logs],
        pagination=PaginationMeta(page=page, limit=limit, total=total, pages=pages),
    )


@router.get("/{log_id}", response_model=AuditLogResponse, summary="Get a single audit log entry")
async def get_audit_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AuditLogResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_AUDIT)
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "Audit log entry not found."}},
        )
    return AuditLogResponse.model_validate(log)
