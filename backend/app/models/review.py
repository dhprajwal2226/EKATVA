"""
app/models/review.py

Human Review model — the central governance decision point.

Person 1 creates material_matches.
Person 2 wraps them in Review records and drives the decision workflow.

BOTH ai_classification and final_classification are preserved.
Human decisions NEVER overwrite AI results.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ReviewStatus(str):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDITED = "EDITED"
    ESCALATED = "ESCALATED"


class ReviewDecision(str):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EDIT = "EDIT"
    ESCALATE = "ESCALATE"


class ReviewPriority(str):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    NORMAL = "NORMAL"


_STATUS_ENUM = SAEnum(
    "PENDING", "IN_REVIEW", "APPROVED", "REJECTED", "EDITED", "ESCALATED",
    name="review_status",
)
_DECISION_ENUM = SAEnum(
    "APPROVE", "REJECT", "EDIT", "ESCALATE",
    name="review_decision",
)
_PRIORITY_ENUM = SAEnum(
    "CRITICAL", "HIGH", "MEDIUM", "NORMAL",
    name="review_priority",
)


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # FK into Person 1's material_matches table (read-only reference)
    match_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    # The reviewer assigned/claimed this review
    reviewer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Escalation fields
    escalated_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Workflow fields
    status: Mapped[str] = mapped_column(
        _STATUS_ENUM, nullable=False, server_default="PENDING", index=True
    )
    decision: Mapped[str | None] = mapped_column(_DECISION_ENUM, nullable=True)
    reviewer_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── AI result — IMMUTABLE after creation ──────────────────────────────────
    original_ai_classification: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(nullable=True)
    ai_recommendation: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Critical conflict flag from Person 1
    has_critical_conflict: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("false")
    )
    critical_conflict_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Human decision — stored alongside AI, NOT replacing it ────────────────
    final_classification: Mapped[str | None] = mapped_column(String(128), nullable=True)
    human_override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # CPSE metadata (snapshot for quick filtering, source from Person 1)
    source_cpse_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    target_cpse_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_material_code: Mapped[str | None] = mapped_column(String(256), nullable=True)
    target_material_code: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Priority for workflow queue
    priority: Mapped[str] = mapped_column(
        _PRIORITY_ENUM, nullable=False, server_default="NORMAL", index=True
    )

    # Linked national material (set after approval)
    national_material_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("national_materials.id", ondelete="SET NULL"), nullable=True
    )

    # Timestamps
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Optimistic concurrency version
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))

    # ── Relationships ──────────────────────────────────────────────────────────
    reviewer: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="reviews", foreign_keys=[reviewer_id]
    )
    history: Mapped[list["ReviewHistory"]] = relationship(
        "ReviewHistory", back_populates="review", cascade="all, delete-orphan"
    )
    national_material: Mapped["NationalMaterial | None"] = relationship(  # type: ignore[name-defined]
        "NationalMaterial", back_populates="source_reviews", foreign_keys=[national_material_id]
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Review id={self.id} match_id={self.match_id} status={self.status}>"


class ReviewHistory(Base):
    """
    Immutable snapshot of a review state transition.
    Append-only — never updated or deleted.
    """
    __tablename__ = "review_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    from_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_status: Mapped[str] = mapped_column(String(64), nullable=False)
    decision: Mapped[str | None] = mapped_column(String(64), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    review: Mapped["Review"] = relationship("Review", back_populates="history")
