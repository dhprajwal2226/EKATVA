"""CPSE Material Mapping Foundation Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
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

    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    national_material = relationship("NationalMaterial", back_populates="cpse_mappings")
    cpse = relationship("CPSE", back_populates="mappings")
    material = relationship("Material", back_populates="cpse_mappings")

    __table_args__ = (
        Index("ix_cpse_material_mapping_nat_mat", "national_material_id", "material_id", unique=True),
    )
