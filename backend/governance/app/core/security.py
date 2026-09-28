"""
app/core/security.py

JWT creation/validation and Argon2 password hashing.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Password hashing ───────────────────────────────────────────────────────────
_pwd_hasher = PasswordHash([Argon2Hasher()])


def hash_password(plain_password: str) -> str:
    """Return Argon2 hash of *plain_password*."""
    return _pwd_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when *plain_password* matches *hashed_password*."""
    try:
        return _pwd_hasher.verify(plain_password, hashed_password)
    except Exception:
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────
_SECRET = settings.JWT_SECRET_KEY
_ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(
    subject: str,
    additional_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a short-lived access token."""
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + delta
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if additional_claims:
        payload.update(additional_claims)
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a longer-lived refresh token."""
    delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + delta
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT.

    Raises JWTError on invalid/expired token.
    Never log the token value.
    """
    return jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])


def decode_access_token(token: str) -> Dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Not an access token")
    return payload


def decode_refresh_token(token: str) -> Dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise JWTError("Not a refresh token")
    return payload
