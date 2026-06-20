"""
api/deps.py
FastAPI dependencies shared across all routes.
"""
from __future__ import annotations

from collections.abc import Generator
import uuid

from fastapi import Depends, Header
from sqlalchemy.orm import Session
import jwt

from db.models.user import RoleEnum, User
from core.config import settings
from db.session import SessionLocal
from repository.user_repository import UserRepository
from services.exceptions import ForbiddenError, UnauthorizedError
from services.security import decode_access_token


def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy session, ensuring it is closed after the request,
    whether the request succeeded or raised an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Convenience alias used in route signatures: db: DB
DB = Depends(get_db)


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing bearer token.")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_access_token(token, settings.AUTH_SECRET)
    except (ValueError, jwt.PyJWTError) as exc:
        raise UnauthorizedError(str(exc)) from exc

    user_id = uuid.UUID(payload["user_id"])
    user = UserRepository(db).get_user_by_id(user_id)
    if user is None:
        raise UnauthorizedError("Invalid token user.")
    return user


def require_role(*allowed_roles: RoleEnum):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError("You do not have permission to perform this action.")
        return current_user

    return dependency
