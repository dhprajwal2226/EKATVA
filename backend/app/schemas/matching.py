"""Pydantic schemas for Hybrid Matching & Explainable Match results."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.conflict import ConflictItem


class MaterialItemReference(BaseModel):
    id: int
    cpse: str
    code: str
    description: str
    normalized_description: Optional[str] = None


class MatchScores(BaseModel):
    semantic: float
    fuzzy: float
    attribute: float
    technical: float
    final: float


class MatchExplanation(BaseModel):
    why_matched: List[str] = []
    what_matched: List[str] = []
    what_differed: List[str] = []
    recommendation: str
    review_required: bool
    confidence: Optional[float] = None
    technical_conflicts: List[ConflictItem] = []


class MatchResponse(BaseModel):
    id: str
    source_material: MaterialItemReference
    target_material: MaterialItemReference
    scores: MatchScores
    classification: str
    technical_conflicts: List[ConflictItem] = []
    explanation: MatchExplanation
    status: str
    review_required: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RunMatchingRequest(BaseModel):
    limit_materials: Optional[int] = Field(default=None, description="Optional cap on materials to process")


class RunMatchingResponse(BaseModel):
    message: str
    total_pairs_evaluated: int
    matches_recorded: int
    conflicts_detected: int
    classifications_tally: Dict[str, int]


class StandaloneMatchRequest(BaseModel):
    source_description: str
    target_description: str


class StandaloneMatchResponse(BaseModel):
    source_description: str
    target_description: str
    scores: MatchScores
    classification: str
    review_required: bool
    recommendation: str
    confidence: float
    technical_conflicts: List[ConflictItem]
    explanation: MatchExplanation


class PaginatedMatchesResponse(BaseModel):
    items: List[MatchResponse]
    total: int
    page: int
    page_size: int
    pages: int
