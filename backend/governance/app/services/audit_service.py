"""
app/services/audit_service.py

Centralized audit logging service.
All important actions flow through log_action().
Audit records are APPEND-ONLY.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_action(
    db: AsyncSession,
    action: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    before_data: Optional[Dict[str, Any]] = None,
    after_data: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """
    Append a new audit entry.

    Never update or delete existing entries.
    If a correction is needed, call this again with a CORRECTION action.
    """
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    if request is not None:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        before_data=before_data,
        after_data=after_data,
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    # Flush so the entry gets an ID within the current transaction
    await db.flush()
    return entry
