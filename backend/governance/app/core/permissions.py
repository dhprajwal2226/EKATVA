"""
app/core/permissions.py

Centralized Role-Based Access Control (RBAC).
All permission checks must go through this module.
NEVER duplicate permission logic inside route handlers.
"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from fastapi import HTTPException, status

if TYPE_CHECKING:
    from app.models.user import User


# ── Roles ─────────────────────────────────────────────────────────────────────
class Role(str, Enum):
    ADMIN = "ADMIN"
    NATIONAL_REVIEWER = "NATIONAL_REVIEWER"
    CPSE_REVIEWER = "CPSE_REVIEWER"
    INVESTIGATOR = "INVESTIGATOR"
    VIEWER = "VIEWER"


# ── Permissions ────────────────────────────────────────────────────────────────
class Permission(str, Enum):
    # User management
    CAN_MANAGE_USERS = "CAN_MANAGE_USERS"

    # Review workflow
    CAN_VIEW_REVIEWS = "CAN_VIEW_REVIEWS"
    CAN_CLAIM_REVIEW = "CAN_CLAIM_REVIEW"
    CAN_APPROVE_MATCH = "CAN_APPROVE_MATCH"
    CAN_REJECT_MATCH = "CAN_REJECT_MATCH"
    CAN_EDIT_MATCH = "CAN_EDIT_MATCH"
    CAN_ESCALATE_REVIEW = "CAN_ESCALATE_REVIEW"
    CAN_RESOLVE_ESCALATION = "CAN_RESOLVE_ESCALATION"

    # National Material Master
    CAN_CREATE_CNMC = "CAN_CREATE_CNMC"
    CAN_ACTIVATE_NATIONAL_MATERIAL = "CAN_ACTIVATE_NATIONAL_MATERIAL"
    CAN_SUSPEND_NATIONAL_MATERIAL = "CAN_SUSPEND_NATIONAL_MATERIAL"
    CAN_DEPRECATE_NATIONAL_MATERIAL = "CAN_DEPRECATE_NATIONAL_MATERIAL"
    CAN_EDIT_NATIONAL_MATERIAL = "CAN_EDIT_NATIONAL_MATERIAL"
    CAN_VIEW_NATIONAL_MATERIAL = "CAN_VIEW_NATIONAL_MATERIAL"

    # Mappings
    CAN_CREATE_MAPPING = "CAN_CREATE_MAPPING"
    CAN_APPROVE_MAPPING = "CAN_APPROVE_MAPPING"
    CAN_REJECT_MAPPING = "CAN_REJECT_MAPPING"
    CAN_VIEW_MAPPINGS = "CAN_VIEW_MAPPINGS"

    # Audit
    CAN_VIEW_AUDIT = "CAN_VIEW_AUDIT"


# ── Role → Permissions mapping ─────────────────────────────────────────────────
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.CAN_MANAGE_USERS,
        Permission.CAN_VIEW_REVIEWS,
        Permission.CAN_CLAIM_REVIEW,
        Permission.CAN_APPROVE_MATCH,
        Permission.CAN_REJECT_MATCH,
        Permission.CAN_EDIT_MATCH,
        Permission.CAN_ESCALATE_REVIEW,
        Permission.CAN_RESOLVE_ESCALATION,
        Permission.CAN_CREATE_CNMC,
        Permission.CAN_ACTIVATE_NATIONAL_MATERIAL,
        Permission.CAN_SUSPEND_NATIONAL_MATERIAL,
        Permission.CAN_DEPRECATE_NATIONAL_MATERIAL,
        Permission.CAN_EDIT_NATIONAL_MATERIAL,
        Permission.CAN_VIEW_NATIONAL_MATERIAL,
        Permission.CAN_CREATE_MAPPING,
        Permission.CAN_APPROVE_MAPPING,
        Permission.CAN_REJECT_MAPPING,
        Permission.CAN_VIEW_MAPPINGS,
        Permission.CAN_VIEW_AUDIT,
    },
    Role.NATIONAL_REVIEWER: {
        Permission.CAN_VIEW_REVIEWS,
        Permission.CAN_CLAIM_REVIEW,
        Permission.CAN_APPROVE_MATCH,
        Permission.CAN_REJECT_MATCH,
        Permission.CAN_EDIT_MATCH,
        Permission.CAN_ESCALATE_REVIEW,
        Permission.CAN_RESOLVE_ESCALATION,
        Permission.CAN_CREATE_CNMC,
        Permission.CAN_ACTIVATE_NATIONAL_MATERIAL,
        Permission.CAN_SUSPEND_NATIONAL_MATERIAL,
        Permission.CAN_DEPRECATE_NATIONAL_MATERIAL,
        Permission.CAN_EDIT_NATIONAL_MATERIAL,
        Permission.CAN_VIEW_NATIONAL_MATERIAL,
        Permission.CAN_CREATE_MAPPING,
        Permission.CAN_APPROVE_MAPPING,
        Permission.CAN_REJECT_MAPPING,
        Permission.CAN_VIEW_MAPPINGS,
        Permission.CAN_VIEW_AUDIT,
    },
    Role.CPSE_REVIEWER: {
        Permission.CAN_VIEW_REVIEWS,
        Permission.CAN_CLAIM_REVIEW,
        # CPSE_REVIEWER can recommend but NOT directly approve national materials
        Permission.CAN_REJECT_MATCH,
        Permission.CAN_EDIT_MATCH,
        Permission.CAN_ESCALATE_REVIEW,
        Permission.CAN_VIEW_NATIONAL_MATERIAL,
        Permission.CAN_VIEW_MAPPINGS,
    },
    Role.INVESTIGATOR: {
        Permission.CAN_VIEW_REVIEWS,
        Permission.CAN_VIEW_NATIONAL_MATERIAL,
        Permission.CAN_VIEW_MAPPINGS,
        Permission.CAN_VIEW_AUDIT,
    },
    Role.VIEWER: {
        Permission.CAN_VIEW_NATIONAL_MATERIAL,
        Permission.CAN_VIEW_MAPPINGS,
    },
}


def has_permission(user: "User", permission: Permission) -> bool:
    """Return True when *user* holds *permission* through their role."""
    try:
        role = Role(user.role)
    except ValueError:
        return False
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_permission(user: "User", permission: Permission) -> None:
    """
    Raise HTTP 403 when *user* does not hold *permission*.
    Use this inside every protected endpoint.
    """
    if not has_permission(user, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "PERMISSION_DENIED",
                    "message": "You do not have permission to perform this action.",
                }
            },
        )


def require_active(user: "User") -> None:
    """Raise HTTP 403 when the user account is inactive."""
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


def require_cpse_access(user: "User", cpse_id: str) -> None:
    """
    Ensure CPSE_REVIEWER only operates on their own CPSE.
    ADMIN and NATIONAL_REVIEWER have unrestricted CPSE access.
    """
    try:
        role = Role(user.role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
            "error": {"code": "PERMISSION_DENIED", "message": "Unknown role."}
        })

    if role == Role.CPSE_REVIEWER:
        if str(user.cpse_id) != str(cpse_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "CPSE_ACCESS_DENIED",
                        "message": "You are not authorized to access records belonging to this CPSE.",
                    }
                },
            )
