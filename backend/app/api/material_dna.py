"""
Material DNA API Routes.
Interactive extraction of technical attributes, dimensions, and identity hashes.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.material_dna_service import MaterialDNAService
from app.schemas.material_dna import MaterialAttributeSchema

router = APIRouter(prefix="/dna", tags=["Material DNA"])


class ExtractDNARequest(BaseModel):
    description: str = Field(..., examples=["SS HEX BOLT M16 X 50 SS304 ASTM A193"])


class ExtractDNAResponse(BaseModel):
    original_description: str
    normalized_description: str
    attributes: MaterialAttributeSchema
    fingerprint_hash: str
    overall_confidence: float


@router.post("/extract", response_model=ExtractDNAResponse, summary="Extract Material DNA from raw description")
def preview_dna_extraction(payload: ExtractDNARequest):
    """
    Deterministically parses physical/engineering properties from text
    without needing an existing database entry.
    """
    dna = MaterialDNAService.extract_dna(payload.description)

    attr_schema = MaterialAttributeSchema(
        material_type=dna.get("material_type"),
        material=dna.get("material"),
        grade=dna.get("grade"),
        size=dna.get("size"),
        diameter=dna.get("diameter"),
        length=dna.get("length"),
        width=dna.get("width"),
        height=dna.get("height"),
        thickness=dna.get("thickness"),
        pressure=dna.get("pressure"),
        schedule=dna.get("schedule"),
        form=dna.get("form"),
        standard=dna.get("standard"),
        application=dna.get("application"),
        manufacturer=dna.get("manufacturer"),
        confidence_scores=dna.get("confidence_scores", {}),
        fingerprint_hash=dna.get("fingerprint_hash"),
    )

    return ExtractDNAResponse(
        original_description=payload.description,
        normalized_description=dna.get("normalized_description", ""),
        attributes=attr_schema,
        fingerprint_hash=dna.get("fingerprint_hash", ""),
        overall_confidence=dna.get("overall_confidence", 0.5),
    )
