"""
app/models/audit_log.py

APPEND-ONLY governance audit trail.

RULES:
  - Normal users MUST NOT update or delete audit logs.
  - If a correction is needed, append a new event.
  - Every important action must record WHO, WHAT, WHEN, WHY, BEFORE, AFTER.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Action code — e.g. LOGIN, MATCH_APPROVED, CNMC_CREATED
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    # Type of entity acted on — e.g. material_match, national_material
    entity_type: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)

    # Before / after snapshots for full lineage
    before_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Human-readable justification for the action
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Request metadata
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # NEVER NULL — every event has a timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    user: Mapped["User | None"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="audit_logs"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuditLog id={self.id} action={self.action} user_id={self.user_id}>"
