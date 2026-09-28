"""Pydantic schemas for Material DNA and technical attributes."""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MaterialAttributeSchema(BaseModel):
    material_type: Optional[str] = None
    material: Optional[str] = None
    grade: Optional[str] = None
    size: Optional[str] = None
    diameter: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    thickness: Optional[float] = None
    pressure: Optional[str] = None
    schedule: Optional[str] = None
    form: Optional[str] = None
    standard: Optional[str] = None
    application: Optional[str] = None
    manufacturer: Optional[str] = None
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    fingerprint_hash: Optional[str] = None

    model_config = {"from_attributes": True}


class MaterialDNAResponse(BaseModel):
    material_id: int
    material_code: str
    original_description: str
    normalized_description: str
    attributes: MaterialAttributeSchema
    fingerprint_hash: str
    overall_confidence: float
