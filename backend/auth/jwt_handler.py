"""
CryptoTrace LEA — JWT Token Handler & User Authentication
Issues signed tokens and validates credentials against canonical user accounts.
"""

import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "cryptotrace-lea-insecure-dev-secret-key-32charsmin")
ALGORITHM = "HS256"
EXPIRATION_HOURS = 8

# Seed Users for LEA Operation
SEED_USERS = {
    "investigator1": {
        "username": "investigator1",
        "full_name": "Inspector R. Sharma",
        "role": "INVESTIGATOR",
        "unit": "Cyber Crime Police Station, Mumbai",
        "password_hash": hashlib.sha256("Password@123".encode()).hexdigest(),
    },
    "supervisor1": {
        "username": "supervisor1",
        "full_name": "ACP V. Deshmukh",
        "role": "SUPERVISOR",
        "unit": "I4C Cyber Coordination Directorate",
        "password_hash": hashlib.sha256("Password@123".encode()).hexdigest(),
    },
    "admin1": {
        "username": "admin1",
        "full_name": "System Administrator",
        "role": "ADMINISTRATOR",
        "unit": "MHA CIS Division",
        "password_hash": hashlib.sha256("Password@123".encode()).hexdigest(),
    },
    "sahyog_service": {
        "username": "sahyog_service",
        "full_name": "SAHYOG Ingestion Agent",
        "role": "INTEGRATION_SERVICE",
        "unit": "I4C Gateway",
        "password_hash": hashlib.sha256("ServiceSecret@2026".encode()).hexdigest(),
    },
}


def authenticate_user(username: str, password_plain: str) -> Optional[Dict[str, Any]]:
    """Authenticates username and password against the secure seed registry."""
    user = SEED_USERS.get(username.strip())
    if not user:
        return None
    hashed = hashlib.sha256(password_plain.encode()).hexdigest()
    if user["password_hash"] == hashed:
        return {
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "unit": user["unit"],
        }
    return None


def create_access_token(user: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates an authoritative signed HS256 JWT access token."""
    from datetime import timezone
    now_utc = datetime.now(timezone.utc)
    expire = now_utc + (expires_delta or timedelta(hours=EXPIRATION_HOURS))
    payload = {
        "sub": user["username"],
        "name": user.get("full_name", user["username"]),
        "role": user["role"],
        "unit": user.get("unit", "LEA Unit"),
        "exp": expire,
        "iat": now_utc,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Validates and decodes JWT token, returning payload dictionary or None if expired/tampered."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None
