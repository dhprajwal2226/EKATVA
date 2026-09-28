"""Material Technical Attributes Model (Material DNA)."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class MaterialAttribute(Base):
    __tablename__ = "material_attributes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material_id = Column(
        Integer,
        ForeignKey("materials.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Core Technical Taxonomy
    material_type = Column(String(100), nullable=True, index=True)  # Pipe, Valve, Bolt, Flange, etc.
    material = Column(String(100), nullable=True, index=True)       # Carbon Steel, Stainless Steel, etc.
    grade = Column(String(100), nullable=True, index=True)          # SS304, SS316, A106 Gr B, etc.
    size = Column(String(100), nullable=True)                       # 10 INCH, M16 X 50, etc.

    # Normalized Dimensions (all in standard mm)
    diameter = Column(Float, nullable=True)                         # mm
    length = Column(Float, nullable=True)                           # mm
    width = Column(Float, nullable=True)                            # mm
    height = Column(Float, nullable=True)                           # mm
    thickness = Column(Float, nullable=True)                        # mm

    # Engineering Specifications
    pressure = Column(String(100), nullable=True)                   # 150#, 300#, 16 bar, etc.
    schedule = Column(String(50), nullable=True)                    # 40, 80, 160, XXS, etc.
    form = Column(String(100), nullable=True)                       # Seamless, Welded, Forged, Hex, etc.

    # Compliance & Context
    standard = Column(String(150), nullable=True, index=True)       # ASTM A106, ASME B16.5, DIN 933, etc.
    application = Column(String(200), nullable=True)                # High Temperature, Cryogenic, etc.
    manufacturer = Column(String(200), nullable=True)

    # Technical metadata and confidence scoring
    other_attributes = Column(JSON, nullable=True, default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    material_rel = relationship("Material", back_populates="attributes")
