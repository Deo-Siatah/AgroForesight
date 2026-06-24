"""
api/v1/auth.py
Login-only auth endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from schemas.auth import LoginRequest, LoginResponse, UserRead
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    return AuthService(db).login(data)


@router.get("/me", response_model=UserRead)
def me(current_user = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)