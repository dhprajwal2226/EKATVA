"""
Normalization API Routes.
Interactive testing and previewing for normalization, abbreviations, and unit conversions.
SIH 2026 - National Material Master Platform.
"""

from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.normalization_service import NormalizationService
from app.utils.text import DOMAIN_ABBREVIATIONS

router = APIRouter(prefix="/normalization", tags=["Normalization & Units"])


class NormalizeRequest(BaseModel):
    description: str = Field(..., examples=["CS PIPE 10 IN SCH40"])


class AbbreviationItem(BaseModel):
    abbr: str
    expansion: str


class DimensionItem(BaseModel):
    original_value: float
    original_unit: str
    normalized_value: float
    normalized_unit: str
    ambiguous: bool


class NormalizeResponse(BaseModel):
    original_description: str
    normalized_description: str
    expanded_abbreviations: List[AbbreviationItem]
    dimensions: List[DimensionItem]


@router.post("/normalize", response_model=NormalizeResponse, summary="Normalize text and preview conversions")
def preview_normalization(payload: NormalizeRequest):
    """
    Test deterministic normalization pipeline:
    Expands domain abbreviations, standardizes multiplication/separators,
    and converts dimensions to standard metric units.
    """
    res = NormalizationService.process_description(payload.description)
    return NormalizeResponse(
        original_description=res["original_description"],
        normalized_description=res["normalized_description"],
        expanded_abbreviations=[
            AbbreviationItem(abbr=item["abbr"], expansion=item["expansion"])
            for item in res["expanded_abbreviations"]
        ],
        dimensions=[
            DimensionItem(
                original_value=d["original_value"],
                original_unit=d["original_unit"],
                normalized_value=d["normalized_value"],
                normalized_unit=d["normalized_unit"],
                ambiguous=d["ambiguous"],
            )
            for d in res["dimensions"]
        ],
    )


@router.get("/abbreviations", response_model=Dict[str, str], summary="List centralized domain abbreviations")
def get_domain_abbreviations():
    """Returns the centralized dictionary of industrial CPSE abbreviations and canonical expansions."""
    return DOMAIN_ABBREVIATIONS
