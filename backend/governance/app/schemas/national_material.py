"""
app/schemas/national_material.py

National Material Master schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NationalMaterialCreate(BaseModel):
    standard_description: str = Field(..., min_length=5)
    category: Optional[str] = None
    canonical_attributes: Dict[str, Any] = Field(default_factory=dict)
    # If provided, a review_id ties the new record to a completed review
    source_review_id: Optional[int] = None


class NationalMaterialUpdate(BaseModel):
    standard_description: Optional[str] = Field(None, min_length=5)
    category: Optional[str] = None
    canonical_attributes: Optional[Dict[str, Any]] = None
    reason: Optional[str] = Field(None, description="Reason for update — stored in history.")


class NationalMaterialResponse(BaseModel):
    id: int
    cnmc: str
    standard_description: str
    category: Optional[str]
    canonical_attributes: Dict[str, Any]
    identity_hash: str
    status: str
    created_by_id: Optional[int]
    approved_by_id: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NationalMaterialDetailResponse(NationalMaterialResponse):
    """Full detail including CPSE mappings."""
    mappings: List["MappingBriefResponse"] = []


class NationalMaterialListResponse(BaseModel):
    items: List[NationalMaterialResponse]
    pagination: "PaginationMeta"


class NationalMaterialHistoryItem(BaseModel):
    id: int
    change_type: str
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    reason: Optional[str]
    changed_by_id: Optional[int]
    timestamp: datetime

    model_config = {"from_attributes": True}


class MappingBriefResponse(BaseModel):
    id: int
    cpse_id: str
    material_id: str
    material_code: Optional[str]
    mapping_type: str
    status: str
    confidence: Optional[float]

    model_config = {"from_attributes": True}


class StatusChangeRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for status change.")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
