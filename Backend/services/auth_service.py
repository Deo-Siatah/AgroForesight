"""
services/auth_service.py
Login and authenticated-user helpers.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from core.config import settings
from db.models.user import User
from repository.user_repository import UserRepository
from schemas.auth import LoginRequest, LoginResponse, UserRead
from services.exceptions import UnauthorizedError
from services.security import create_access_token, verify_password


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def login(self, data: LoginRequest) -> LoginResponse:
        user = self.repo.get_user_by_email(data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")

        token = create_access_token(
            {"user_id": str(user.id), "role": user.role.value},
            secret=settings.AUTH_SECRET,
            ttl_minutes=settings.AUTH_TOKEN_TTL_MINUTES,
        )
        return LoginResponse(access_token=token, user=UserRead.model_validate(user))

    def get_user(self, user: User) -> UserRead:
        return UserRead.model_validate(user)