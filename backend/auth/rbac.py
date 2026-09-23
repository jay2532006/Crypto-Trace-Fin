"""
CryptoTrace LEA — Role-Based Access Control (RBAC)
Defines canonical roles, action permission matrices, and access boundaries.
"""

from typing import Set, Dict
from backend.models.confidence_types import UserRole

# Canonical Permission Matrix
ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    "INVESTIGATOR": {
        "cases:create",
        "cases:read",
        "cases:update",
        "trace:execute",
        "findings:read",
        "evidence:read",
        "evidence:verify",
        "notices:draft",
        "notices:submit",
        "reports:export",
    },
    "SUPERVISOR": {
        "cases:create",
        "cases:read",
        "cases:update",
        "cases:assign",
        "trace:execute",
        "findings:read",
        "evidence:read",
        "evidence:verify",
        "notices:draft",
        "notices:submit",
        "notices:approve",
        "notices:reject",
        "reports:export",
        "audit:read",
        "cases:close",
    },
    "ADMINISTRATOR": {
        "cases:create",
        "cases:read",
        "cases:update",
        "cases:assign",
        "trace:execute",
        "findings:read",
        "evidence:read",
        "evidence:verify",
        "notices:draft",
        "notices:submit",
        "notices:approve",
        "notices:reject",
        "reports:export",
        "audit:read",
        "system:manage",
        "users:manage",
        "config:read",
    },
    "INTEGRATION_SERVICE": {
        "cases:create",
        "cases:read",
        "trace:execute",
        "evidence:read",
    },
}


def has_permission(role: str, permission: str) -> bool:
    """Checks whether the assigned role holds the required action permission."""
    perms = ROLE_PERMISSIONS.get(role, set())  # type: ignore
    return permission in perms
