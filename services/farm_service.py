"""
services/farm_service.py
Business brain for the Farm entity.
Bad farm data = bad AI later — coordinate validation is the
highest-leverage check in Phase 1 (plan rule 8).
"""
from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models.farm import Farm
from db.models.user import RoleEnum, User
from repository.farm_repository import FarmRepository
from repository.farmer_repository import FarmerRepository
from schemas.farm import FarmCreate, FarmRead
from services.exceptions import BusinessRuleError, ForbiddenError, NotFoundError


class FarmService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmRepository(db)
        self.farmer_repo = FarmerRepository(db)

    def create_farm(self, data: FarmCreate, current_user: User) -> FarmRead:
        """
        Persist a new farm after verifying the owning farmer exists.
        Coordinate and acreage validation is already handled by FarmCreate
        (including the Kenya bounding-box check).
        """
        farmer = self.farmer_repo.get_farmer_by_id(data.farmer_id)
        if farmer is None:
            raise NotFoundError(f"Farmer '{data.farmer_id}' not found.")

        if current_user.role != RoleEnum.admin and current_user.sacco_id != farmer.sacco_id:
            raise ForbiddenError("You can only create farms for your own SACCO.")

        farm = Farm(
            id=uuid.uuid4(),
            farmer_id=data.farmer_id,
            name=data.name,
            county=data.county,
            acreage=data.acreage,
            latitude=data.latitude,
            longitude=data.longitude,
        )
        self.repo.create_farm(farm)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise BusinessRuleError("Unable to create farm due to conflicting data.") from exc
        self.db.refresh(farm)
        return FarmRead.model_validate(farm)

    def get_farm(self, farm_id: uuid.UUID, current_user: User) -> FarmRead:
        farm = self.repo.get_farm(farm_id)
        if farm is None:
            raise NotFoundError(f"Farm '{farm_id}' not found.")

        if current_user.role == RoleEnum.farmer:
            if current_user.farmer_id != farm.farmer_id:
                raise ForbiddenError("You can only view your own farms.")
        elif current_user.role != RoleEnum.admin and current_user.sacco_id != farm.farmer.sacco_id:
            raise ForbiddenError("You can only view farms in your own SACCO.")

        return FarmRead.model_validate(farm)
