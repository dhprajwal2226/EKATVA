"""
app/schemas/review.py

Schemas for the human review workflow.
Both AI result and human decision fields are present.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    """
    Person 1 creates a material_match; Person 2 wraps it in a Review.
    """
    match_id: str = Field(..., description="Person 1's material_match identifier")
    original_ai_classification: Optional[str] = None
    ai_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_recommendation: Optional[str] = None
    has_critical_conflict: bool = False
    critical_conflict_details: Optional[Dict[str, Any]] = None
    source_cpse_id: Optional[str] = None
    target_cpse_id: Optional[str] = None
    source_material_code: Optional[str] = None
    target_material_code: Optional[str] = None
    priority: Optional[str] = "NORMAL"


class ReviewApproveRequest(BaseModel):
    comment: Optional[str] = Field(
        None, description="Required when a critical conflict exists."
    )
    final_classification: Optional[str] = None
    # Explicit acknowledgement field for critical conflicts
    conflict_acknowledged: bool = Field(
        False,
        description="Must be True when approving a review with critical conflicts.",
    )


class ReviewRejectRequest(BaseModel):
    reason: str = Field(..., min_length=10, description="Mandatory rejection reason.")
    final_classification: Optional[str] = None


class ReviewEditRequest(BaseModel):
    """
    Reviewer edits classification / attributes.
    AI result is preserved; only final_classification and human fields are changed.
    """
    final_classification: str = Field(..., description="Human-corrected classification.")
    human_override_reason: str = Field(..., min_length=5)
    reviewer_comment: Optional[str] = None


class ReviewEscalateRequest(BaseModel):
    escalation_reason: str = Field(..., min_length=10)


class ReviewHistoryItem(BaseModel):
    id: int
    from_status: Optional[str]
    to_status: str
    decision: Optional[str]
    comment: Optional[str]
    changed_by_id: Optional[int]
    timestamp: datetime

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    id: int
    match_id: str
    reviewer_id: Optional[int]
    status: str
    decision: Optional[str]
    reviewer_comment: Optional[str]
    rejection_reason: Optional[str]

    # AI fields — immutable after creation
    original_ai_classification: Optional[str]
    ai_confidence: Optional[float]
    ai_recommendation: Optional[str]
    has_critical_conflict: bool
    critical_conflict_details: Optional[Dict[str, Any]]

    # Human decision fields
    final_classification: Optional[str]
    human_override_reason: Optional[str]

    source_cpse_id: Optional[str]
    target_cpse_id: Optional[str]
    source_material_code: Optional[str]
    target_material_code: Optional[str]

    priority: str
    national_material_id: Optional[int]

    escalated_by_id: Optional[int]
    escalated_at: Optional[datetime]
    escalation_reason: Optional[str]
    resolved_by_id: Optional[int]
    resolved_at: Optional[datetime]
    resolution: Optional[str]

    reviewed_at: Optional[datetime]
    claimed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    version: int

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    items: List[ReviewResponse]
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
