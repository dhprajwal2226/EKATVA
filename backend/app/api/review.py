from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.audit_log import AuditLog
from app.models.review import (
    Review,
    ReviewDecision,
    ReviewHistory,
    ReviewPriority,
    ReviewStatus,
)
from app.models.user import User
from app.schemas.review import (
    ReviewActionRequest,
    ReviewDetailResponse,
    ReviewResponse,
)

router = APIRouter(prefix="/v1/reviews", tags=["Governance / Reviews"])


def _record_audit_log(
    db: Session,
    user_id: int,
    action: str,
    entity_id: str,
    reason: Optional[str] = None,
    before_data: Optional[dict] = None,
    after_data: Optional[dict] = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type="review",
        entity_id=entity_id,
        reason=reason,
        before_data=before_data,
        after_data=after_data,
    )
    db.add(audit_log)


@router.get("/", response_model=list[ReviewResponse])
def list_reviews(
    status: Optional[str] = Query(None, description="Filter by status (e.g. PENDING, APPROVED)"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List reviews in the queue."""
    query = db.query(Review)
    if status:
        query = query.filter(Review.status == status)
    if priority:
        query = query.filter(Review.priority == priority)
    
    # Empty db should safely return []
    return query.all()


@router.get("/{review_id}", response_model=ReviewDetailResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detail and history for a specific review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    return review


@router.post("/{review_id}/approve", response_model=ReviewDetailResponse)
def approve_review(
    review_id: int,
    payload: ReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    
    if review.status == ReviewStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review is already approved",
        )
    
    before_snapshot = {
        "status": review.status,
        "decision": review.decision,
    }

    old_status = review.status
    review.status = ReviewStatus.APPROVED
    review.decision = ReviewDecision.APPROVE
    review.reviewer_comment = payload.comment
    review.reviewer_id = current_user.id
    review.reviewed_at = datetime.now(timezone.utc)
    review.version += 1

    db.flush()

    after_snapshot = {
        "status": review.status,
        "decision": review.decision,
    }

    history = ReviewHistory(
        review_id=review.id,
        changed_by_id=current_user.id,
        from_status=old_status,
        to_status=review.status,
        decision=review.decision,
        comment=payload.comment,
        snapshot=after_snapshot,
    )
    db.add(history)

    _record_audit_log(
        db=db,
        user_id=current_user.id,
        action="MATCH_APPROVED",
        entity_id=str(review.id),
        reason=payload.comment,
        before_data=before_snapshot,
        after_data=after_snapshot,
    )

    db.commit()
    db.refresh(review)
    return review


@router.post("/{review_id}/reject", response_model=ReviewDetailResponse)
def reject_review(
    review_id: int,
    payload: ReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    
    if review.status == ReviewStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review is already rejected",
        )
    
    before_snapshot = {
        "status": review.status,
        "decision": review.decision,
    }

    old_status = review.status
    review.status = ReviewStatus.REJECTED
    review.decision = ReviewDecision.REJECT
    review.rejection_reason = payload.comment
    review.reviewer_id = current_user.id
    review.reviewed_at = datetime.now(timezone.utc)
    review.version += 1

    db.flush()

    after_snapshot = {
        "status": review.status,
        "decision": review.decision,
    }

    history = ReviewHistory(
        review_id=review.id,
        changed_by_id=current_user.id,
        from_status=old_status,
        to_status=review.status,
        decision=review.decision,
        comment=payload.comment,
        snapshot=after_snapshot,
    )
    db.add(history)

    _record_audit_log(
        db=db,
        user_id=current_user.id,
        action="MATCH_REJECTED",
        entity_id=str(review.id),
        reason=payload.comment,
        before_data=before_snapshot,
        after_data=after_snapshot,
    )

    db.commit()
    db.refresh(review)
    return review


@router.post("/{review_id}/escalate", response_model=ReviewDetailResponse)
def escalate_review(
    review_id: int,
    payload: ReviewActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Escalate a review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    
    if review.status == ReviewStatus.ESCALATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review is already escalated",
        )
    
    before_snapshot = {
        "status": review.status,
        "decision": review.decision,
    }

    old_status = review.status
    review.status = ReviewStatus.ESCALATED
    review.decision = ReviewDecision.ESCALATE
    review.escalation_reason = payload.comment
    review.escalated_by_id = current_user.id
    review.escalated_at = datetime.now(timezone.utc)
    if payload.resolution:
        review.resolution = payload.resolution
    review.version += 1

    db.flush()

    after_snapshot = {
        "status": review.status,
        "decision": review.decision,
    }

    history = ReviewHistory(
        review_id=review.id,
        changed_by_id=current_user.id,
        from_status=old_status,
        to_status=review.status,
        decision=review.decision,
        comment=payload.comment,
        snapshot=after_snapshot,
    )
    db.add(history)

    _record_audit_log(
        db=db,
        user_id=current_user.id,
        action="MATCH_ESCALATED",
        entity_id=str(review.id),
        reason=payload.comment,
        before_data=before_snapshot,
        after_data=after_snapshot,
    )

    db.commit()
    db.refresh(review)
    return review
