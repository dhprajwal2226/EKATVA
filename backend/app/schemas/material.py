"""Pydantic schemas for Material master records."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.material_dna import MaterialAttributeSchema


class MaterialBase(BaseModel):
    material_code: str
    original_description: str
    normalized_description: Optional[str] = None
    category: Optional[str] = None
    source_reference: Optional[str] = None
    status: str = "INGESTED"


class MaterialSummary(BaseModel):
    id: int
    cpse_code: str
    material_code: str
    original_description: str
    normalized_description: Optional[str] = None
    category: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MaterialDetailResponse(BaseModel):
    id: int
    cpse_id: int
    cpse_code: str
    cpse_name: str
    material_code: str
    original_description: str
    normalized_description: Optional[str] = None
    category: Optional[str] = None
    source_reference: Optional[str] = None
    status: str
    attributes: Optional[MaterialAttributeSchema] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedMaterialsResponse(BaseModel):
    items: List[MaterialSummary]
    total: int
    page: int
    page_size: int
    pages: int
