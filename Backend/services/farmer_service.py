"""
services/farmer_service.py
Business brain for the Farmer entity.
- register_farmer: duplicate-checks then persists
- get_farmer_profile: composite Farmer + Farms + Loans response
"""
from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models.farmer import Farmer
from db.models.sacco import Sacco
from db.models.user import RoleEnum, User
from repository.farmer_repository import FarmerRepository
from repository.user_repository import UserRepository
from schemas.farmer import FarmerCreate, FarmerRead, FarmerProfile
from schemas.farm import FarmRead
from schemas.loan import LoanRead
from services.exceptions import ConflictError, DuplicateError, ForbiddenError, NotFoundError
from services.security import hash_password


class FarmerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmerRepository(db)
        self.user_repo = UserRepository(db)

    def register_farmer(self, data: FarmerCreate, current_user: User) -> FarmerRead:
        """
        Validate uniqueness then persist.
        Raises DuplicateError if phone or national_id already exists.
        """
        if current_user.role == RoleEnum.sacco_admin and current_user.sacco_id != data.sacco_id:
            raise ForbiddenError("You can only register farmers for your own SACCO.")

        if current_user.role not in (RoleEnum.admin, RoleEnum.sacco_admin):
            raise ForbiddenError("Only admins and sacco admins can register farmers.")

        if self.db.get(Sacco, data.sacco_id) is None:
            raise NotFoundError(f"Sacco '{data.sacco_id}' not found.")

        if self.repo.get_farmer_by_phone(data.phone):
            raise DuplicateError(f"A farmer with phone '{data.phone}' is already registered.")

        if data.national_id and self.repo.get_farmer_by_national_id(data.national_id):
            raise DuplicateError(
                f"A farmer with national ID '{data.national_id}' is already registered."
            )

        farmer = Farmer(
            id=uuid.uuid4(),
            sacco_id=data.sacco_id,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            national_id=data.national_id,
        )
        self.repo.create_farmer(farmer)
        if self.user_repo.get_user_by_email(data.login_email) is not None:
            raise ConflictError(f"User '{data.login_email}' already exists.")

        self.user_repo.create_user(User(
            id=uuid.uuid4(),
            email=data.login_email,
            password_hash=hash_password(data.login_password),
            sacco_id=data.sacco_id,
            farmer_id=farmer.id,
            role=RoleEnum.farmer,
        ))
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateError(
                "A farmer with that phone or national ID already exists."
            ) from exc
        self.db.refresh(farmer)
        return FarmerRead.model_validate(farmer)

    def list_farmers(
        self,
        current_user: User,
        *,
        sacco_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[FarmerRead]:
        """
        Return a paginated list of farmers.
        - admin: may filter by any sacco_id or see all.
        - sacco_admin: always scoped to their own SACCO regardless of the sacco_id param.
        """
        if current_user.role == RoleEnum.sacco_admin:
            effective_sacco = current_user.sacco_id
        else:
            effective_sacco = sacco_id

        farmers = self.repo.list_farmers(
            sacco_id=effective_sacco, offset=offset, limit=limit
        )
        return [FarmerRead.model_validate(f) for f in farmers]

    def get_farmer_profile(self, farmer_id: uuid.UUID, current_user: User) -> FarmerProfile:
        """
        Return Farmer + all Farms + all Loans in a single composite object.
        Designed to feed the farmer dashboard, WhatsApp agent, and USSD layer.
        """
        farmer = self.repo.get_farmer_by_id(farmer_id)
        if farmer is None:
            raise NotFoundError(f"Farmer '{farmer_id}' not found.")

        if current_user.role == RoleEnum.sacco_admin and current_user.sacco_id != farmer.sacco_id:
            raise ForbiddenError("You can only view farmers in your own SACCO.")

        if current_user.role == RoleEnum.farmer and current_user.farmer_id != farmer_id:
            raise ForbiddenError("You can only view your own farmer profile.")

        if current_user.role not in (RoleEnum.admin, RoleEnum.sacco_admin, RoleEnum.farmer):
            raise ForbiddenError("You do not have permission to view farmer profiles.")

        farms = self.repo.get_farmer_farms(farmer_id)
        loans = self.repo.get_farmer_loans(farmer_id)

        return FarmerProfile(
            farmer=FarmerRead.model_validate(farmer),
            farms=[FarmRead.model_validate(f) for f in farms],
            loans=[LoanRead.model_validate(l) for l in loans],
        )
