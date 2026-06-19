"""
Repository layer — Farm
Responsibility: DB access ONLY. No validation, no business logic.
"""
from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from db.models.farm import Farm
from db.models.season import Season


class FarmRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_farm(self, farm: Farm) -> Farm:
        """Insert a new Farm row. Caller is responsible for all validation."""
        self.db.add(farm)
        self.db.flush()
        return farm

    # ------------------------------------------------------------------
    # Read — single record
    # ------------------------------------------------------------------

    def get_farm(self, farm_id: uuid.UUID) -> Farm | None:
        return self.db.get(Farm, farm_id)

    # ------------------------------------------------------------------
    # Read — collections
    # ------------------------------------------------------------------

    def list_farms(
        self,
        *,
        farmer_id: uuid.UUID | None = None,
        county: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Farm]:
        """Return a paginated slice of farms, optionally filtered."""
        q = self.db.query(Farm)
        if farmer_id is not None:
            q = q.filter(Farm.farmer_id == farmer_id)
        if county is not None:
            q = q.filter(Farm.county == county)
        return q.offset(offset).limit(limit).all()

    def get_farm_seasons(self, farm_id: uuid.UUID) -> List[Season]:
        return (
            self.db.query(Season)
            .filter(Season.farm_id == farm_id)
            .all()
        )
