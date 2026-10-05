"""CPSE workflow roles (SIH 2026 - National Material Master Platform)."""
from enum import Enum


class Role(str, Enum):
    CPSE_STEWARD = "CPSE_STEWARD"          # maker: submits/maps materials for own CPSE
    MATERIAL_REVIEWER = "MATERIAL_REVIEWER"  # checker: approves/rejects matches and CNMCs
    NATIONAL_ADMIN = "NATIONAL_ADMIN"      # manages the national catalogue across CPSEs
    AUDITOR = "AUDITOR"                    # read-only access to audit logs
