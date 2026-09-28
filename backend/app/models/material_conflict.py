"""Material Technical Conflict Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class MaterialConflict(Base):
    __tablename__ = "material_conflicts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(
        Integer,
        ForeignKey("material_matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    attribute = Column(String(100), nullable=False, index=True)  # grade, diameter, pressure, schedule, standard
    source_value = Column(String(255), nullable=True)
    target_value = Column(String(255), nullable=True)
    
    severity = Column(
        String(50),
        nullable=False,
        default="MINOR",
        index=True,
    )  # INFO, MINOR, MAJOR, CRITICAL
    
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    match = relationship("MaterialMatch", back_populates="conflicts")

    __table_args__ = (
        Index("ix_conflicts_severity_attribute", "severity", "attribute"),
    )
