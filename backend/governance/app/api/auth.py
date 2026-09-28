"""
app/api/auth.py

Authentication routes — thin, delegates all logic to auth_service.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LogoutRequest, MeResponse, RefreshRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with employee ID or email + password",
    responses={
        401: {"description": "Invalid credentials"},
        403: {"description": "Account inactive"},
    },
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Returns access_token (short-lived) and refresh_token (longer-lived).
    Authentication failure returns a generic 401 — no account enumeration.
    """
    return await auth_service.login(payload, db, request)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange a valid refresh token for a new access token",
)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await auth_service.refresh_access_token(payload, db)


@router.post(
    "/logout",
    summary="Logout (client-side token invalidation)",
    status_code=200,
)
async def logout(
    payload: LogoutRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Since we use stateless JWT, logout is primarily a client-side action.
    This endpoint exists for audit logging and future refresh-token blocklist support.
    """
    return {"message": "Logged out successfully."}


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Return the currently authenticated user's profile",
)
async def me(
    current_user: User = Depends(get_current_user),
) -> MeResponse:
    return auth_service.build_me_response(current_user)
