"""
app/schemas/user.py

User request/response schemas.
password_hash is NEVER exposed in any response.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.config import settings
from app.core.permissions import Role


class UserCreate(BaseModel):
    employee_id: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=1, max_length=256)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=32)
    password: str = Field(..., min_length=12)
    role: Role
    department: Optional[str] = Field(None, max_length=256)
    cpse_id: Optional[str] = Field(None, max_length=64)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < settings.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters."
            )
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=32)
    role: Optional[Role] = None
    department: Optional[str] = Field(None, max_length=256)
    cpse_id: Optional[str] = Field(None, max_length=64)


class UserResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: str
    phone: Optional[str]
    role: str
    department: Optional[str]
    cpse_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserResponse]
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
