"""
app/schemas/auth.py

Request/response schemas for authentication endpoints.
NEVER include password_hash in any response.
"""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Accept either employee_id or email alongside password."""
    login: str = Field(
        ...,
        description="Employee ID or email address",
        examples=["EMP001", "reviewer@iocl.gov.in"],
    )
    password: str = Field(..., min_length=1, description="User password")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token TTL in seconds")


class MeResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: str
    role: str
    department: str | None
    cpse_id: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
