"""
services/farmer_service.py
Business brain for the Farmer entity.
- register_farmer: duplicate-checks then persists
- get_farmer_profile: composite Farmer + Farms + Loans response
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from db.models.farmer import Farmer
from repository.farmer_repository import FarmerRepository
from schemas.farmer import FarmerCreate, FarmerRead, FarmerProfile
from schemas.farm import FarmRead
from schemas.loan import LoanRead
from services.exceptions import DuplicateError, NotFoundError


class FarmerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FarmerRepository(db)

    def register_farmer(self, data: FarmerCreate) -> FarmerRead:
        """
        Validate uniqueness then persist.
        Raises DuplicateError if phone or national_id already exists.
        """
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
        self.db.commit()
        self.db.refresh(farmer)
        return FarmerRead.model_validate(farmer)

    def get_farmer_profile(self, farmer_id: uuid.UUID) -> FarmerProfile:
        """
        Return Farmer + all Farms + all Loans in a single composite object.
        Designed to feed the farmer dashboard, WhatsApp agent, and USSD layer.
        """
        farmer = self.repo.get_farmer_by_id(farmer_id)
        if farmer is None:
            raise NotFoundError(f"Farmer '{farmer_id}' not found.")

        farms = self.repo.get_farmer_farms(farmer_id)
        loans = self.repo.get_farmer_loans(farmer_id)

        return FarmerProfile(
            farmer=FarmerRead.model_validate(farmer),
            farms=[FarmRead.model_validate(f) for f in farms],
            loans=[LoanRead.model_validate(l) for l in loans],
        )
