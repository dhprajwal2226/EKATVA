"""
app/services/auth_service.py

Authentication business logic.

Security invariants:
  - Passwords are NEVER logged.
  - JWT tokens are NEVER logged.
  - Generic 401 is returned for all auth failures (no account enumeration).
  - last_login_at is updated on successful login.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, MeResponse, RefreshRequest, TokenResponse
from app.services.audit_service import log_action

logger = logging.getLogger(__name__)

_GENERIC_AUTH_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={
        "error": {
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid credentials. Please check your login and password.",
        }
    },
    headers={"WWW-Authenticate": "Bearer"},
)


async def login(
    payload: LoginRequest,
    db: AsyncSession,
    request: Optional[Request] = None,
) -> TokenResponse:
    # Look up by employee_id OR email
    result = await db.execute(
        select(User).where(
            or_(User.employee_id == payload.login, User.email == payload.login)
        )
    )
    user: Optional[User] = result.scalar_one_or_none()

    # Always run verify_password to prevent timing-based enumeration
    dummy_hash = "$argon2id$v=19$m=65536,t=3,p=4$dummy$dummy"
    candidate_hash = user.password_hash if user else dummy_hash

    if not verify_password(payload.password, candidate_hash) or user is None:
        # Log failed attempt without revealing credential details
        logger.warning("Failed login attempt for login='%s'", payload.login)
        raise _GENERIC_AUTH_ERROR

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "ACCOUNT_INACTIVE",
                    "message": "Your account is inactive. Contact an administrator.",
                }
            },
        )

    # Update last login timestamp
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(last_login_at=datetime.now(timezone.utc))
    )

    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"role": user.role, "cpse_id": user.cpse_id},
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    await log_action(
        db=db,
        action="LOGIN",
        user_id=user.id,
        entity_type="user",
        entity_id=str(user.id),
        after_data={"employee_id": user.employee_id, "role": user.role},
        request=request,
    )
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def refresh_access_token(
    payload: RefreshRequest,
    db: AsyncSession,
) -> TokenResponse:
    try:
        token_data = decode_refresh_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Refresh token is invalid or expired.",
                }
            },
        )

    user_id = token_data.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user: Optional[User] = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "User not found or inactive.",
                }
            },
        )

    new_access = create_access_token(
        subject=str(user.id),
        additional_claims={"role": user.role, "cpse_id": user.cpse_id},
    )
    new_refresh = create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def build_me_response(user: User) -> MeResponse:
    return MeResponse(
        id=user.id,
        employee_id=user.employee_id,
        name=user.name,
        email=user.email,
        role=user.role,
        department=user.department,
        cpse_id=user.cpse_id,
        is_active=user.is_active,
    )
