"""National Material Master Model (CNMC Identity)."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class NationalMaterial(Base):
    __tablename__ = "national_materials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cnmc = Column(String(50), nullable=False, unique=True, index=True)  # e.g., CNMC-000001
    standard_description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    canonical_attributes = Column(JSON, nullable=False, default=dict)
    
    # SHA-256 deterministic fingerprint of technical attributes
    identity_hash = Column(String(64), nullable=False, unique=True, index=True)
    
    status = Column(
        String(50),
        nullable=False,
        default="DRAFT",
        index=True,
    )  # DRAFT, VALIDATED, ACTIVE, DEPRECATED

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    cpse_mappings = relationship("CPSEMaterialMapping", back_populates="national_material", cascade="all, delete-orphan")
