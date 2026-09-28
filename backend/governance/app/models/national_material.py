"""
app/models/national_material.py

National Material Master — the governed, CNMC-keyed canonical record.

identity_hash and cnmc have UNIQUE constraints at the DB level.
No application-only enforcement.
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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


_NM_STATUS_ENUM = SAEnum(
    "DRAFT", "PENDING_APPROVAL", "ACTIVE", "SUSPENDED", "DEPRECATED",
    name="national_material_status",
)


class NationalMaterial(Base):
    __tablename__ = "national_materials"
    __table_args__ = (
        UniqueConstraint("cnmc", name="uq_national_material_cnmc"),
        UniqueConstraint("identity_hash", name="uq_national_material_identity_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # The governed national code — generated deterministically
    cnmc: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    standard_description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)

    # JSON bag of canonical technical attributes
    canonical_attributes: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # SHA-256 of the canonical representation — prevents duplicates
    identity_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    status: Mapped[str] = mapped_column(
        _NM_STATUS_ENUM, nullable=False, default="DRAFT", index=True
    )

    # Governance trail
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
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
    created_by: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[created_by_id]
    )
    approved_by: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", foreign_keys=[approved_by_id]
    )
    mappings: Mapped[list["CPSEMaterialMapping"]] = relationship(  # type: ignore[name-defined]
        "CPSEMaterialMapping", back_populates="national_material", cascade="all, delete-orphan"
    )
    source_reviews: Mapped[list["Review"]] = relationship(  # type: ignore[name-defined]
        "Review", back_populates="national_material", foreign_keys="[Review.national_material_id]"
    )
    history: Mapped[list["NationalMaterialHistory"]] = relationship(
        "NationalMaterialHistory", back_populates="national_material", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NationalMaterial cnmc={self.cnmc} status={self.status}>"


class NationalMaterialHistory(Base):
    """
    Append-only version snapshot for NationalMaterial.
    Preserves previous canonical_attributes, description, status.
    """
    __tablename__ = "national_material_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    national_material_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("national_materials.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    changed_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    change_type: Mapped[str] = mapped_column(String(64), nullable=False)  # CREATED, UPDATED, STATUS_CHANGED
    before_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    national_material: Mapped["NationalMaterial"] = relationship(
        "NationalMaterial", back_populates="history"
    )
