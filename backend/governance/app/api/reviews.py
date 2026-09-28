"""
app/api/reviews.py

Human review workflow routes.
Every route enforces permission before delegating to review_service.
"""
from __future__ import annotations

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import Permission, require_active, require_permission
from app.models.user import User
from app.schemas.review import (
    PaginationMeta,
    ReviewApproveRequest,
    ReviewCreateRequest,
    ReviewEditRequest,
    ReviewEscalateRequest,
    ReviewHistoryItem,
    ReviewListResponse,
    ReviewRejectRequest,
    ReviewResponse,
)
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["Human Review Workflow"])


@router.get("", response_model=ReviewListResponse, summary="List review queue with filters")
async def list_reviews(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="PENDING|IN_REVIEW|APPROVED|REJECTED|EDITED|ESCALATED"),
    cpse: Optional[str] = Query(None, description="Filter by source or target CPSE"),
    reviewer_id: Optional[int] = Query(None),
    classification: Optional[str] = Query(None, description="AI classification filter"),
    priority: Optional[str] = Query(None, description="CRITICAL|HIGH|MEDIUM|NORMAL"),
    search: Optional[str] = Query(None, description="Search match ID or material codes"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewListResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_REVIEWS)
    reviews, total = await review_service.list_reviews(
        db, page, limit, status, cpse, reviewer_id, classification, priority, search
    )
    pages = math.ceil(total / limit) if total else 0
    return ReviewListResponse(
        items=[ReviewResponse.model_validate(r) for r in reviews],
        pagination=PaginationMeta(page=page, limit=limit, total=total, pages=pages),
    )


@router.get("/{review_id}", response_model=ReviewResponse, summary="Get review detail")
async def get_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_REVIEWS)
    from sqlalchemy import select
    from app.models.review import Review
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if review is None:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND,
                            detail={"error": {"code": "NOT_FOUND", "message": "Review not found."}})
    return ReviewResponse.model_validate(review)


@router.post("", response_model=ReviewResponse, status_code=201, summary="Create a review from an AI match")
async def create_review(
    payload: ReviewCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_REVIEWS)
    review = await review_service.create_review(payload, db, created_by=current_user, request=request)
    return ReviewResponse.model_validate(review)


@router.post("/{review_id}/claim", response_model=ReviewResponse, summary="Claim a PENDING review")
async def claim_review(
    review_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_CLAIM_REVIEW)
    review = await review_service.claim_review(review_id, db, reviewer=current_user, request=request)
    return ReviewResponse.model_validate(review)


@router.post("/{review_id}/approve", response_model=ReviewResponse, summary="Approve a match")
async def approve_review(
    review_id: int,
    payload: ReviewApproveRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """
    Critical conflict rule: if review has_critical_conflict=True,
    conflict_acknowledged MUST be True and comment MUST be provided.
    """
    require_active(current_user)
    require_permission(current_user, Permission.CAN_APPROVE_MATCH)
    review = await review_service.approve_review(review_id, payload, db, reviewer=current_user, request=request)
    return ReviewResponse.model_validate(review)


@router.post("/{review_id}/reject", response_model=ReviewResponse, summary="Reject a match")
async def reject_review(
    review_id: int,
    payload: ReviewRejectRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_REJECT_MATCH)
    review = await review_service.reject_review(review_id, payload, db, reviewer=current_user, request=request)
    return ReviewResponse.model_validate(review)


@router.post("/{review_id}/edit", response_model=ReviewResponse, summary="Edit AI classification (human override)")
async def edit_review(
    review_id: int,
    payload: ReviewEditRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """
    Human override preserves AI original_ai_classification.
    final_classification is stored as the human decision.
    """
    require_active(current_user)
    require_permission(current_user, Permission.CAN_EDIT_MATCH)
    review = await review_service.edit_review(review_id, payload, db, reviewer=current_user, request=request)
    return ReviewResponse.model_validate(review)


@router.post("/{review_id}/escalate", response_model=ReviewResponse, summary="Escalate to senior reviewer")
async def escalate_review(
    review_id: int,
    payload: ReviewEscalateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_ESCALATE_REVIEW)
    review = await review_service.escalate_review(review_id, payload, db, reviewer=current_user, request=request)
    return ReviewResponse.model_validate(review)


@router.get("/{review_id}/history", response_model=list[ReviewHistoryItem], summary="Get review decision history")
async def get_review_history(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ReviewHistoryItem]:
    require_active(current_user)
    require_permission(current_user, Permission.CAN_VIEW_REVIEWS)
    from sqlalchemy import select
    from app.models.review import ReviewHistory
    result = await db.execute(
        select(ReviewHistory)
        .where(ReviewHistory.review_id == review_id)
        .order_by(ReviewHistory.timestamp.asc())
    )
    history = result.scalars().all()
    return [ReviewHistoryItem.model_validate(h) for h in history]
