"""Material Master Database Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cpse_id = Column(Integer, ForeignKey("cpse.id", ondelete="CASCADE"), nullable=False, index=True)
    material_code = Column(String(100), nullable=False, index=True)
    
    # CRITICAL: original_description MUST NEVER be overwritten.
    original_description = Column(Text, nullable=False)
    normalized_description = Column(Text, nullable=True)
    
    category = Column(String(100), nullable=True, index=True)
    source_reference = Column(String(255), nullable=True)
    status = Column(String(50), default="INGESTED", nullable=False, index=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    cpse = relationship("CPSE", back_populates="materials")
    attributes = relationship("MaterialAttribute", back_populates="material_rel", uselist=False, cascade="all, delete-orphan")
    embedding = relationship("MaterialEmbedding", back_populates="material", uselist=False, cascade="all, delete-orphan")
    
    source_matches = relationship(
        "MaterialMatch",
        foreign_keys="MaterialMatch.source_material_id",
        back_populates="source_material",
        cascade="all, delete-orphan"
    )
    target_matches = relationship(
        "MaterialMatch",
        foreign_keys="MaterialMatch.target_material_id",
        back_populates="target_material",
        cascade="all, delete-orphan"
    )
    cpse_mappings = relationship("CPSEMaterialMapping", back_populates="material", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_materials_cpse_code", "cpse_id", "material_code", unique=True),
        Index("ix_materials_category_status", "category", "status"),
    )
