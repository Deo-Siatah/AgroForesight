"""
services/season_service.py
Business brain for the Season entity.

Valid status transitions (enforced here, never in the repository):
    PLANNED → ACTIVE     (activate_season)
    ACTIVE  → HARVESTED  (harvest_season)
    ACTIVE  → FAILED     (fail_season)

A Season is the container for every downstream AI workflow
(recommendations, weather, monitoring, risk, yield).
"""
from __future__ import annotations

import uuid
from typing import Set

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models.season import Season, SeasonStatusEnum
from repository.season_repository import SeasonRepository
from repository.farm_repository import FarmRepository
from schemas.season import SeasonCreate, SeasonRead
from services.exceptions import BusinessRuleError, InvalidTransitionError, NotFoundError


# Allowed (from → {valid targets}) — extend here as business rules evolve.
_TRANSITIONS: dict[SeasonStatusEnum, Set[SeasonStatusEnum]] = {
    SeasonStatusEnum.planned:   {SeasonStatusEnum.active},
    SeasonStatusEnum.active:    {SeasonStatusEnum.harvested, SeasonStatusEnum.failed},
    SeasonStatusEnum.harvested: set(),   # terminal
    SeasonStatusEnum.failed:    set(),   # terminal
}


class SeasonService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SeasonRepository(db)
        self.farm_repo = FarmRepository(db)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_season(self, data: SeasonCreate) -> SeasonRead:
        """
        Persist a new season for a farm.
        Date ordering is already validated by SeasonCreate.
        Season always starts as PLANNED.
        """
        if self.farm_repo.get_farm(data.farm_id) is None:
            raise NotFoundError(f"Farm '{data.farm_id}' not found.")

        season = Season(
            id=uuid.uuid4(),
            farm_id=data.farm_id,
            crop_type=data.crop_type,
            planting_date=data.planting_date,
            expected_harvest_date=data.expected_harvest_date,
            status=SeasonStatusEnum.planned,
        )
        self.repo.create_season(season)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise BusinessRuleError("Unable to create season due to conflicting data.") from exc
        self.db.refresh(season)
        return SeasonRead.model_validate(season)

    def get_season(self, season_id: uuid.UUID) -> SeasonRead:
        season = self.repo.get_season(season_id)
        if season is None:
            raise NotFoundError(f"Season '{season_id}' not found.")
        return SeasonRead.model_validate(season)

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------

    def activate_season(self, season_id: uuid.UUID) -> SeasonRead:
        """PLANNED → ACTIVE"""
        return self._transition(season_id, SeasonStatusEnum.active)

    def harvest_season(self, season_id: uuid.UUID) -> SeasonRead:
        """ACTIVE → HARVESTED"""
        return self._transition(season_id, SeasonStatusEnum.harvested)

    def fail_season(self, season_id: uuid.UUID) -> SeasonRead:
        """ACTIVE → FAILED"""
        return self._transition(season_id, SeasonStatusEnum.failed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _transition(self, season_id: uuid.UUID, target: SeasonStatusEnum) -> SeasonRead:
        season = self.repo.get_season(season_id)
        if season is None:
            raise NotFoundError(f"Season '{season_id}' not found.")

        allowed = _TRANSITIONS.get(season.status, set())
        if target not in allowed:
            raise InvalidTransitionError(
                f"Cannot move season from '{season.status.value}' to '{target.value}'. "
                f"Allowed transitions: {[s.value for s in allowed] or 'none (terminal state)'}."
            )

        season.status = target
        self.repo.update_season(season)
        self.db.commit()
        self.db.refresh(season)
        return SeasonRead.model_validate(season)
