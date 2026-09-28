"""Pydantic schemas for technical conflicts."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ConflictItem(BaseModel):
    id: Optional[int] = None
    attribute: str
    source_value: Optional[str] = None
    target_value: Optional[str] = None
    severity: str  # INFO, MINOR, MAJOR, CRITICAL
    reason: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConflictDetailResponse(BaseModel):
    id: int
    match_id: int
    attribute: str
    source_value: Optional[str] = None
    target_value: Optional[str] = None
    severity: str
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedConflictsResponse(BaseModel):
    items: List[ConflictDetailResponse]
    total: int
    page: int
    page_size: int
    pages: int
