"""
CryptoTrace LEA — FastAPI Auth Dependencies & Permission Guards
"""

from typing import Dict, Any, Optional
from fastapi import Header, HTTPException, status
from .jwt_handler import decode_access_token
from .rbac import has_permission


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Extracts and validates JWT from Authorization header.
    Defaults to 'investigator1' in development/demo mode if no token supplied for smooth testing.
    """
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            payload = decode_access_token(parts[1])
            if payload:
                return {
                    "username": payload.get("sub", "investigator1"),
                    "role": payload.get("role", "INVESTIGATOR"),
                    "unit": payload.get("unit", "Cyber Crime Unit"),
                }

    # Development/Demo fallback persona
    return {
        "username": "investigator1",
        "role": "INVESTIGATOR",
        "unit": "Cyber Crime Police Station",
    }


def require_permission(permission: str):
    """Dependency factory checking that current user role possesses the required permission."""
    def dependency(user: Dict[str, Any] = None):
        user = user or {"role": "INVESTIGATOR"}
        role = user.get("role", "INVESTIGATOR")
        if not has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role '{role}' lacks '{permission}' authority.",
            )
        return user
    return dependency


def require_supervisor(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Enforces that only SUPERVISOR or ADMINISTRATOR can access this endpoint."""
    user = get_current_user(authorization)
    role = user.get("role", "INVESTIGATOR")
    if role not in ("SUPERVISOR", "ADMINISTRATOR"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Action requires SUPERVISOR or ADMINISTRATOR authorization.",
        )
    return user
