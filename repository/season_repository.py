"""
Repository layer — Season
Responsibility: DB access ONLY. No validation, no business logic.
Status transitions are enforced in the Season Service, not here.
"""
from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from db.models.season import Season, SeasonStatusEnum
from db.models.farm import Farm
from db.models.farmer import Farmer


class SeasonRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_season(self, season: Season) -> Season:
        """Insert a new Season row. Caller is responsible for all validation."""
        self.db.add(season)
        self.db.flush()
        return season

    def update_season(self, season: Season) -> Season:
        """Persist changes to an already-attached Season instance."""
        self.db.flush()
        return season

    # ------------------------------------------------------------------
    # Read — single record
    # ------------------------------------------------------------------

    def get_season(self, season_id: uuid.UUID) -> Season | None:
        return self.db.get(Season, season_id)

    # ------------------------------------------------------------------
    # Read — collections
    # ------------------------------------------------------------------

    def list_farm_seasons(
        self,
        farm_id: uuid.UUID,
        *,
        status: SeasonStatusEnum | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Season]:
        """Return paginated seasons for a farm, optionally filtered by status."""
        q = self.db.query(Season).filter(Season.farm_id == farm_id)
        if status is not None:
            q = q.filter(Season.status == status)
        return q.offset(offset).limit(limit).all()

    def list_seasons(
        self,
        *,
        sacco_id: uuid.UUID | None = None,
        status: SeasonStatusEnum | None = None,
        crop_type: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Season]:
        """Return a global paginated list of seasons with optional filters."""
        q = (
            self.db.query(Season)
            .join(Farm, Season.farm_id == Farm.id)
            .join(Farmer, Farm.farmer_id == Farmer.id)
        )
        if sacco_id is not None:
            q = q.filter(Farmer.sacco_id == sacco_id)
        if status is not None:
            q = q.filter(Season.status == status)
        if crop_type is not None:
            q = q.filter(Season.crop_type.ilike(f"%{crop_type}%"))
        return q.offset(offset).limit(limit).all()
