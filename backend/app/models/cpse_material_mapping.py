"""CPSE Material Mapping Foundation Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Float
from sqlalchemy.orm import relationship
from app.db.database import Base


class CPSEMaterialMapping(Base):
    __tablename__ = "cpse_material_mapping"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    national_material_id = Column(
        Integer,
        ForeignKey("national_materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cpse_id = Column(Integer, ForeignKey("cpse.id"), nullable=False, index=True)
    material_id = Column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    mapping_type = Column(
        String(50),
        nullable=False,
        default="IDENTICAL",
    )  # IDENTICAL, NEAR_DUPLICATE, FUNCTIONALLY_EQUIVALENT
    
    material_code = Column(String(256), nullable=True)
    confidence = Column(Float, nullable=True)
    
    source_match_id = Column(Integer, ForeignKey("material_matches.id", ondelete="SET NULL"), nullable=True, index=True)
    
    status = Column(
        String(50),
        nullable=False,
        default="PROPOSED",
        index=True,
    )  # PROPOSED, ACTIVE, REJECTED, DEPRECATED

    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    national_material = relationship("NationalMaterial", back_populates="cpse_mappings")
    cpse = relationship("CPSE", back_populates="mappings")
    material = relationship("Material", back_populates="cpse_mappings")
    approved_by_user = relationship("User", foreign_keys=[approved_by_id])
    source_match = relationship("MaterialMatch", foreign_keys=[source_match_id])

    __table_args__ = (
        Index("ix_cpse_material_mapping_nat_mat", "national_material_id", "material_id", unique=True),
    )
