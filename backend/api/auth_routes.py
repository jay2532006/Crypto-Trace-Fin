"""
CryptoTrace LEA — Authentication Routes
Endpoints:
- POST /api/v1/auth/login
- GET  /api/v1/auth/me
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.auth.jwt_handler import authenticate_user, create_access_token
from backend.auth.decorators import get_current_user

router = APIRouter(tags=["Auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/api/v1/auth/login")
@router.post("/api/v1/login")
def login(req: LoginRequest):
    """Authenticates LEA credentials and issues signed JWT bearer token."""
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.get("username"),
        "role": user.get("role"),
        "unit": user.get("unit"),
        "user": user,
    }


@router.get("/api/v1/auth/me")
@router.get("/api/v1/me")
def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns currently authenticated investigator/supervisor persona."""
    return current_user
