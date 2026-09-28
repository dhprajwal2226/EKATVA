"""
app/models/cpse_material_mapping.py

Maps a CPSE's own material code to a CNMC national material identity.

CRITICAL RULE: The original CPSE material code is NEVER modified.
               CNMC is an ADDITIONAL reference layer.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


_MAPPING_TYPE_ENUM = SAEnum(
    "IDENTICAL", "NEAR_DUPLICATE", "FUNCTIONALLY_EQUIVALENT",
    name="mapping_type",
)
_MAPPING_STATUS_ENUM = SAEnum(
    "PROPOSED", "ACTIVE", "REJECTED", "DEPRECATED",
    name="mapping_status",
)


class CPSEMaterialMapping(Base):
    __tablename__ = "cpse_material_mapping"
    __table_args__ = (
        # Prevent duplicate (national_material, cpse, material) combinations
        UniqueConstraint(
            "national_material_id", "cpse_id", "material_id",
            name="uq_cpse_material_mapping",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    national_material_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("national_materials.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # The CPSE owning the material (e.g., "IOCL", "NTPC", "BHEL")
    cpse_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Person 1's source material ID — read-only reference
    material_id: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    # Original CPSE material code — NEVER modified
    material_code: Mapped[str | None] = mapped_column(String(256), nullable=True)

    mapping_type: Mapped[str] = mapped_column(_MAPPING_TYPE_ENUM, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Source match from Person 1's material_matches table
    source_match_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)

    status: Mapped[str] = mapped_column(
        _MAPPING_STATUS_ENUM, nullable=False, default="PROPOSED", index=True
    )

    approved_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    national_material: Mapped["NationalMaterial"] = relationship(  # type: ignore[name-defined]
        "NationalMaterial", back_populates="mappings"
    )
    approved_by: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[approved_by_id]
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<CPSEMaterialMapping cpse={self.cpse_id} "
            f"material={self.material_id} status={self.status}>"
        )
