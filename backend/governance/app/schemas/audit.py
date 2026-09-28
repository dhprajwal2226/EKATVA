"""
app/schemas/audit.py

Audit log response schemas.
Audit logs are read-only from the API layer.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    reason: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditListResponse(BaseModel):
    items: List[AuditLogResponse]
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
