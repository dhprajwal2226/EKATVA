from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.review import ReviewDecision, ReviewPriority, ReviewStatus


class ReviewHistoryResponse(BaseModel):
    id: int
    review_id: int
    changed_by_id: Optional[int] = None
    from_status: Optional[str] = None
    to_status: str
    decision: Optional[str] = None
    comment: Optional[str] = None
    snapshot: Optional[dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    match_id: str
    reviewer_id: Optional[int] = None
    escalated_by_id: Optional[int] = None
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    resolved_by_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    status: str
    decision: Optional[str] = None
    reviewer_comment: Optional[str] = None
    rejection_reason: Optional[str] = None
    original_ai_classification: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_recommendation: Optional[str] = None
    has_critical_conflict: bool
    critical_conflict_details: Optional[dict[str, Any]] = None
    final_classification: Optional[str] = None
    human_override_reason: Optional[str] = None
    source_cpse_id: Optional[str] = None
    target_cpse_id: Optional[str] = None
    source_material_code: Optional[str] = None
    target_material_code: Optional[str] = None
    priority: str
    national_material_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    version: int


class ReviewResponse(ReviewBase):
    id: int

    class Config:
        from_attributes = True


class ReviewDetailResponse(ReviewResponse):
    history: list[ReviewHistoryResponse] = Field(default_factory=list)


class ReviewActionRequest(BaseModel):
    comment: Optional[str] = Field(None, description="Comment or reason for the decision")
    resolution: Optional[str] = Field(None, description="Resolution if escalated")
