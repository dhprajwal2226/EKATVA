"""
app/schemas/mapping.py

CPSE material mapping schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MappingCreate(BaseModel):
    cpse_id: str = Field(..., description="CPSE identifier (e.g., IOCL, NTPC, BHEL)")
    material_id: str = Field(..., description="Person 1's material identifier")
    material_code: Optional[str] = Field(
        None, description="Original CPSE material code — never modified."
    )
    mapping_type: str = Field(..., description="IDENTICAL | NEAR_DUPLICATE | FUNCTIONALLY_EQUIVALENT")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    source_match_id: Optional[str] = None


class MappingUpdate(BaseModel):
    mapping_type: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    reason: Optional[str] = None


class MappingResponse(BaseModel):
    id: int
    national_material_id: int
    cpse_id: str
    material_id: str
    material_code: Optional[str]
    mapping_type: str
    confidence: Optional[float]
    source_match_id: Optional[str]
    status: str
    approved_by_id: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MappingListResponse(BaseModel):
    items: List[MappingResponse]
    pagination: "PaginationMeta"


class MappingStatusRequest(BaseModel):
    reason: Optional[str] = None


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
