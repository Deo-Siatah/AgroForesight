"""
Repository layer — User
Responsibility: DB access ONLY. No validation, no business logic.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from db.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id) -> User | None:
        return self.db.get(User, user_id)
