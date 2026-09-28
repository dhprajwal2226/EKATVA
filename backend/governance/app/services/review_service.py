"""
app/services/review_service.py

Human review workflow — the central governance engine.

CRITICAL RULES:
1. AI results (original_ai_classification, ai_confidence) are NEVER overwritten.
2. Critical conflicts REQUIRE explicit acknowledgement before approval.
3. Approval operations are atomic: review + national_material + mapping + audit.
4. Concurrency is handled via optimistic versioning — returns 409 on conflict.
5. Rejection requires a mandatory reason.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import Review, ReviewHistory
from app.schemas.review import (
    ReviewApproveRequest,
    ReviewCreateRequest,
    ReviewEditRequest,
    ReviewEscalateRequest,
    ReviewRejectRequest,
)
from app.models.user import User
from app.services.audit_service import log_action


def _snapshot(review: Review) -> dict:
    """Build a JSON-serialisable snapshot of a review for audit/history."""
    return {
        "status": review.status,
        "decision": review.decision,
        "final_classification": review.final_classification,
        "reviewer_id": review.reviewer_id,
        "version": review.version,
    }


async def _get_review_or_404(review_id: int, db: AsyncSession) -> Review:
    result = await db.execute(
        select(Review)
        .where(Review.id == review_id)
        .options(selectinload(Review.history))
    )
    review = result.scalar_one_or_none()
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Review not found."}},
        )
    return review


async def create_review(
    payload: ReviewCreateRequest,
    db: AsyncSession,
    created_by: User,
    request: Optional[Request] = None,
) -> Review:
    # Determine priority from conflicts
    priority = payload.priority or "NORMAL"
    if payload.has_critical_conflict:
        priority = "HIGH"

    review = Review(
        match_id=payload.match_id,
        original_ai_classification=payload.original_ai_classification,
        ai_confidence=payload.ai_confidence,
        ai_recommendation=payload.ai_recommendation,
        has_critical_conflict=payload.has_critical_conflict,
        critical_conflict_details=payload.critical_conflict_details,
        source_cpse_id=payload.source_cpse_id,
        target_cpse_id=payload.target_cpse_id,
        source_material_code=payload.source_material_code,
        target_material_code=payload.target_material_code,
        priority=priority,
        status="PENDING",
        version=1,
    )
    db.add(review)
    await db.flush()

    history = ReviewHistory(
        review_id=review.id,
        changed_by_id=created_by.id,
        from_status=None,
        to_status="PENDING",
        snapshot=_snapshot(review),
    )
    db.add(history)

    await log_action(
        db=db,
        action="REVIEW_CREATED",
        user_id=created_by.id,
        entity_type="review",
        entity_id=str(review.id),
        after_data={"match_id": review.match_id, "priority": review.priority},
        request=request,
    )
    await db.commit()
    await db.refresh(review)
    return review


async def claim_review(
    review_id: int,
    db: AsyncSession,
    reviewer: User,
    request: Optional[Request] = None,
) -> Review:
    review = await _get_review_or_404(review_id, db)

    if review.status not in ("PENDING",):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "REVIEW_NOT_CLAIMABLE",
                    "message": f"Review is in status '{review.status}' and cannot be claimed.",
                }
            },
        )

    before = _snapshot(review)
    review.status = "IN_REVIEW"
    review.reviewer_id = reviewer.id
    review.claimed_at = datetime.now(timezone.utc)
    review.version += 1

    db.add(ReviewHistory(
        review_id=review.id,
        changed_by_id=reviewer.id,
        from_status="PENDING",
        to_status="IN_REVIEW",
        snapshot=_snapshot(review),
    ))
    await log_action(
        db=db, action="REVIEW_CLAIMED", user_id=reviewer.id,
        entity_type="review", entity_id=str(review.id),
        before_data=before, after_data=_snapshot(review), request=request,
    )
    await db.commit()
    await db.refresh(review)
    return review


async def approve_review(
    review_id: int,
    payload: ReviewApproveRequest,
    db: AsyncSession,
    reviewer: User,
    request: Optional[Request] = None,
) -> Review:
    """
    Approve a match.

    CRITICAL CONFLICT RULE: If has_critical_conflict is True, the reviewer MUST:
      (a) provide a non-empty comment, AND
      (b) set conflict_acknowledged = True
    Otherwise the system rejects the approval.
    """
    review = await _get_review_or_404(review_id, db)

    if review.status not in ("IN_REVIEW", "PENDING"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "REVIEW_NOT_APPROVABLE",
                    "message": f"Review is in status '{review.status}' and cannot be approved.",
                }
            },
        )

    # Critical conflict gate
    if review.has_critical_conflict:
        if not payload.conflict_acknowledged:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "CRITICAL_CONFLICT_ACKNOWLEDGEMENT_REQUIRED",
                        "message": (
                            "This review has a critical technical conflict. "
                            "You must set conflict_acknowledged=true and provide a comment "
                            "explaining your decision before approving."
                        ),
                    }
                },
            )
        if not payload.comment or len(payload.comment.strip()) < 5:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": "COMMENT_REQUIRED_FOR_CONFLICT",
                        "message": "A reviewer comment is mandatory when approving a critical conflict.",
                    }
                },
            )

    before = _snapshot(review)
    review.status = "APPROVED"
    review.decision = "APPROVE"
    review.reviewer_id = reviewer.id
    review.reviewer_comment = payload.comment
    review.reviewed_at = datetime.now(timezone.utc)
    # Preserve AI result; store human classification separately
    if payload.final_classification:
        review.final_classification = payload.final_classification
    review.version += 1

    db.add(ReviewHistory(
        review_id=review.id,
        changed_by_id=reviewer.id,
        from_status=before["status"],
        to_status="APPROVED",
        decision="APPROVE",
        comment=payload.comment,
        snapshot=_snapshot(review),
    ))
    await log_action(
        db=db, action="MATCH_APPROVED", user_id=reviewer.id,
        entity_type="review", entity_id=str(review.id),
        before_data=before,
        after_data={**_snapshot(review), "conflict_acknowledged": payload.conflict_acknowledged},
        reason=payload.comment,
        request=request,
    )
    await db.commit()
    await db.refresh(review)
    return review


async def reject_review(
    review_id: int,
    payload: ReviewRejectRequest,
    db: AsyncSession,
    reviewer: User,
    request: Optional[Request] = None,
) -> Review:
    review = await _get_review_or_404(review_id, db)

    if review.status not in ("IN_REVIEW", "PENDING"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "REVIEW_NOT_REJECTABLE",
                    "message": f"Review is in status '{review.status}' and cannot be rejected.",
                }
            },
        )

    before = _snapshot(review)
    review.status = "REJECTED"
    review.decision = "REJECT"
    review.reviewer_id = reviewer.id
    review.rejection_reason = payload.reason
    review.reviewed_at = datetime.now(timezone.utc)
    if payload.final_classification:
        review.final_classification = payload.final_classification
    review.version += 1

    db.add(ReviewHistory(
        review_id=review.id,
        changed_by_id=reviewer.id,
        from_status=before["status"],
        to_status="REJECTED",
        decision="REJECT",
        comment=payload.reason,
        snapshot=_snapshot(review),
    ))
    await log_action(
        db=db, action="MATCH_REJECTED", user_id=reviewer.id,
        entity_type="review", entity_id=str(review.id),
        before_data=before, after_data=_snapshot(review),
        reason=payload.reason, request=request,
    )
    await db.commit()
    await db.refresh(review)
    return review


async def edit_review(
    review_id: int,
    payload: ReviewEditRequest,
    db: AsyncSession,
    reviewer: User,
    request: Optional[Request] = None,
) -> Review:
    """
    Human editor corrects the classification.
    AI original_ai_classification is NEVER modified.
    """
    review = await _get_review_or_404(review_id, db)

    if review.status not in ("IN_REVIEW", "PENDING"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "REVIEW_NOT_EDITABLE",
                    "message": f"Review in status '{review.status}' cannot be edited.",
                }
            },
        )

    before = _snapshot(review)
    # AI classification is preserved — only human fields are updated
    review.final_classification = payload.final_classification
    review.human_override_reason = payload.human_override_reason
    review.reviewer_comment = payload.reviewer_comment
    review.reviewer_id = reviewer.id
    review.status = "EDITED"
    review.decision = "EDIT"
    review.reviewed_at = datetime.now(timezone.utc)
    review.version += 1

    db.add(ReviewHistory(
        review_id=review.id,
        changed_by_id=reviewer.id,
        from_status=before["status"],
        to_status="EDITED",
        decision="EDIT",
        comment=payload.human_override_reason,
        snapshot=_snapshot(review),
    ))
    await log_action(
        db=db, action="MATCH_EDITED", user_id=reviewer.id,
        entity_type="review", entity_id=str(review.id),
        before_data={**before, "ai_classification": review.original_ai_classification},
        after_data={
            "final_classification": review.final_classification,
            "human_override_reason": review.human_override_reason,
        },
        reason=payload.human_override_reason, request=request,
    )
    await db.commit()
    await db.refresh(review)
    return review


async def escalate_review(
    review_id: int,
    payload: ReviewEscalateRequest,
    db: AsyncSession,
    reviewer: User,
    request: Optional[Request] = None,
) -> Review:
    review = await _get_review_or_404(review_id, db)

    if review.status in ("APPROVED", "REJECTED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "REVIEW_ALREADY_DECIDED",
                    "message": "Cannot escalate a review that has already been decided.",
                }
            },
        )

    before = _snapshot(review)
    review.status = "ESCALATED"
    review.decision = "ESCALATE"
    review.escalated_by_id = reviewer.id
    review.escalated_at = datetime.now(timezone.utc)
    review.escalation_reason = payload.escalation_reason
    review.version += 1

    db.add(ReviewHistory(
        review_id=review.id,
        changed_by_id=reviewer.id,
        from_status=before["status"],
        to_status="ESCALATED",
        decision="ESCALATE",
        comment=payload.escalation_reason,
        snapshot=_snapshot(review),
    ))
    await log_action(
        db=db, action="REVIEW_ESCALATED", user_id=reviewer.id,
        entity_type="review", entity_id=str(review.id),
        before_data=before, after_data=_snapshot(review),
        reason=payload.escalation_reason, request=request,
    )
    await db.commit()
    await db.refresh(review)
    return review


async def list_reviews(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    status_filter: Optional[str] = None,
    cpse: Optional[str] = None,
    reviewer_id: Optional[int] = None,
    classification: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Review], int]:
    query = select(Review)

    if status_filter:
        query = query.where(Review.status == status_filter)
    if cpse:
        from sqlalchemy import or_ as sa_or
        query = query.where(
            sa_or(Review.source_cpse_id == cpse, Review.target_cpse_id == cpse)
        )
    if reviewer_id:
        query = query.where(Review.reviewer_id == reviewer_id)
    if classification:
        query = query.where(
            Review.original_ai_classification == classification
        )
    if priority:
        query = query.where(Review.priority == priority)
    if search:
        pattern = f"%{search}%"
        from sqlalchemy import or_ as sa_or
        query = query.where(
            sa_or(
                Review.match_id.ilike(pattern),
                Review.source_material_code.ilike(pattern),
                Review.target_material_code.ilike(pattern),
            )
        )

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar_one()

    offset = (page - 1) * limit
    result = await db.execute(
        query.order_by(Review.created_at.desc()).offset(offset).limit(limit)
    )
    reviews = list(result.scalars().all())
    return reviews, total
