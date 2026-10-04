"""
app/models/user.py

User model — governs authentication, roles, and CPSE scoping.
Password hashes are stored, NEVER plain text.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # NEVER store plain text — only Argon2 hash
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)

    # Role — validated against app.core.permissions.Role
    role: Mapped[str] = mapped_column(String(64), nullable=False)

    department: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Scopes the reviewer to a single CPSE; NULL = unrestricted
    cpse_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────────
    reviews: Mapped[list["Review"]] = relationship(  # type: ignore[name-defined]
        "Review", back_populates="reviewer", foreign_keys="[Review.reviewer_id]"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(  # type: ignore[name-defined]
        "AuditLog", back_populates="user"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} employee_id={self.employee_id} role={self.role}>"
