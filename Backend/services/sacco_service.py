"""
services/sacco_service.py
Business brain for the Sacco entity.
"""
from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models.sacco import Sacco
from db.models.user import RoleEnum, User
from repository.sacco_repository import SaccoRepository
from repository.user_repository import UserRepository
from schemas.sacco import SaccoCreate, SaccoRead
from services.exceptions import BusinessRuleError, ConflictError, ForbiddenError, NotFoundError
from services.security import hash_password


class SaccoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SaccoRepository(db)
        self.user_repo = UserRepository(db)

    def create_sacco(self, data: SaccoCreate, current_user: User) -> SaccoRead:
        if current_user.role != RoleEnum.admin:
            raise ForbiddenError("Only platform admins can create SACCOs.")
        sacco = Sacco(
            id=uuid.uuid4(),
            name=data.name,
            county=data.county,
        )
        self.repo.create_sacco(sacco)
        if self.user_repo.get_user_by_email(data.admin_email) is not None:
            raise ConflictError(f"User '{data.admin_email}' already exists.")

        self.user_repo.create_user(User(
            id=uuid.uuid4(),
            email=data.admin_email,
            password_hash=hash_password(data.admin_password),
            sacco_id=sacco.id,
            farmer_id=None,
            role=RoleEnum.sacco_admin,
        ))
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise BusinessRuleError("Unable to create sacco due to conflicting data.") from exc
        self.db.refresh(sacco)
        return SaccoRead.model_validate(sacco)

    def get_sacco(self, sacco_id: uuid.UUID) -> SaccoRead:
        sacco = self.repo.get_sacco(sacco_id)
        if sacco is None:
            raise NotFoundError(f"Sacco '{sacco_id}' not found.")
        return SaccoRead.model_validate(sacco)

    def list_saccos(self, *, search: str | None = None, offset: int = 0, limit: int = 20) -> list[SaccoRead]:
        return [SaccoRead.model_validate(s) for s in self.repo.list_saccos(search=search, offset=offset, limit=limit)]