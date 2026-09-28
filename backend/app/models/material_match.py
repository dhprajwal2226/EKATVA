"""Material Match Database Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class MaterialMatch(Base):
    __tablename__ = "material_matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_material_id = Column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_material_id = Column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Hybrid Scores
    semantic_score = Column(Float, nullable=False, default=0.0)
    fuzzy_score = Column(Float, nullable=False, default=0.0)
    attribute_score = Column(Float, nullable=False, default=0.0)
    technical_score = Column(Float, nullable=False, default=0.0)
    final_score = Column(Float, nullable=False, default=0.0)

    # Classification & Review Status
    classification = Column(
        String(50),
        nullable=False,
        default="REVIEW_REQUIRED",
        index=True,
    )  # IDENTICAL, NEAR_DUPLICATE, FUNCTIONALLY_EQUIVALENT, DIFFERENT, REVIEW_REQUIRED
    
    status = Column(
        String(50),
        nullable=False,
        default="PENDING_REVIEW",
        index=True,
    )  # PENDING_REVIEW, APPROVED, REJECTED, EDITED

    review_required = Column(Boolean, nullable=False, default=True, index=True)

    # Explainable Matching Payload (why_matched, what_matched, what_differed, recommendation)
    explanation = Column(JSON, nullable=True, default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    source_material = relationship("Material", foreign_keys=[source_material_id], back_populates="source_matches")
    target_material = relationship("Material", foreign_keys=[target_material_id], back_populates="target_matches")
    conflicts = relationship("MaterialConflict", back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_match_source_target", "source_material_id", "target_material_id", unique=True),
        Index("ix_match_classification_status", "classification", "status"),
    )
