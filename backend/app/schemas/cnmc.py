"""Pydantic schemas for CNMC (Common National Material Code) & CPSE Mappings."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CreateCNMCRequest(BaseModel):
    material_ids: List[int] = Field(..., min_length=1, description="List of approved material IDs to cluster under CNMC")
    category: Optional[str] = None


class CPSEMappingSummary(BaseModel):
    id: int
    cpse_code: str
    material_id: int
    material_code: str
    original_description: str
    mapping_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CNMCDetailResponse(BaseModel):
    id: int
    cnmc: str
    standard_description: str
    category: Optional[str] = None
    canonical_attributes: Dict[str, Any]
    identity_hash: str
    status: str
    created_at: datetime
    updated_at: datetime
    mappings: List[CPSEMappingSummary] = []

    model_config = {"from_attributes": True}


class CanonicalDescriptionSelectionResponse(BaseModel):
    selected_material_id: int
    selected_material_code: str
    cpse_code: str
    standard_description: str
    score: float
    reason: List[str]


class PaginatedCNMCResponse(BaseModel):
    items: List[CNMCDetailResponse]
    total: int
    page: int
    page_size: int
    pages: int
