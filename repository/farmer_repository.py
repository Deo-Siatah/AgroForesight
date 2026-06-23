"""
Repository layer — Farmer
Responsibility: DB access ONLY. No validation, no business logic.
"""
from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from db.models.farmer import Farmer
from db.models.farm import Farm
from db.models.loan import Loan


class FarmerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_farmer(self, farmer: Farmer) -> Farmer:
        """Insert a new Farmer row. Caller is responsible for all validation."""
        self.db.add(farmer)
        self.db.flush()  # get generated PK before commit
        return farmer

    # ------------------------------------------------------------------
    # Read — single record
    # ------------------------------------------------------------------

    def get_farmer_by_id(self, farmer_id: uuid.UUID) -> Farmer | None:
        return self.db.get(Farmer, farmer_id)

    def get_farmer_by_phone(self, phone: str) -> Farmer | None:
        return (
            self.db.query(Farmer)
            .filter(Farmer.phone == phone)
            .first()
        )

    def get_farmer_by_national_id(self, national_id: str) -> Farmer | None:
        return (
            self.db.query(Farmer)
            .filter(Farmer.national_id == national_id)
            .first()
        )

    # ------------------------------------------------------------------
    # Read — collections
    # ------------------------------------------------------------------

    def list_farmers(
        self,
        *,
        sacco_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Farmer]:
        """Return a paginated slice of farmers, optionally scoped to a SACCO."""
        q = self.db.query(Farmer)
        if sacco_id is not None:
            q = q.filter(Farmer.sacco_id == sacco_id)
        return q.offset(offset).limit(limit).all()

    def get_farmer_farms(self, farmer_id: uuid.UUID) -> List[Farm]:
        return (
            self.db.query(Farm)
            .filter(Farm.farmer_id == farmer_id)
            .all()
        )

    def get_farmer_loans(self, farmer_id: uuid.UUID) -> List[Loan]:
        return (
            self.db.query(Loan)
            .filter(Loan.farmer_id == farmer_id)
            .all()
        )
