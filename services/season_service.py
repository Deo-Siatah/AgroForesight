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
from db.models.user import RoleEnum, User
from repository.season_repository import SeasonRepository
from repository.farm_repository import FarmRepository
from schemas.season import SeasonCreate, SeasonRead
from services.exceptions import BusinessRuleError, ForbiddenError, InvalidTransitionError, NotFoundError


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

    def create_season(self, data: SeasonCreate, current_user: User) -> SeasonRead:
        """
        Persist a new season for a farm.
        Date ordering is already validated by SeasonCreate.
        Season always starts as PLANNED.
        """
        farm = self.farm_repo.get_farm(data.farm_id)
        if farm is None:
            raise NotFoundError(f"Farm '{data.farm_id}' not found.")

        if current_user.role != RoleEnum.admin and current_user.sacco_id != farm.farmer.sacco_id:
            raise ForbiddenError("You can only create seasons for your own SACCO.")

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

    def get_season(self, season_id: uuid.UUID, current_user: User) -> SeasonRead:
        season = self.repo.get_season(season_id)
        if season is None:
            raise NotFoundError(f"Season '{season_id}' not found.")

        if current_user.role != RoleEnum.admin and current_user.sacco_id != season.farm.farmer.sacco_id:
            raise ForbiddenError("You can only view seasons in your own SACCO.")

        return SeasonRead.model_validate(season)

    def list_seasons(
        self,
        current_user: User,
        *,
        status: SeasonStatusEnum | None = None,
        crop_type: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[SeasonRead]:
        """Return a paginated list of seasons scoped to the caller's SACCO (or all for admin)."""
        sacco_id = None if current_user.role == RoleEnum.admin else current_user.sacco_id
        seasons = self.repo.list_seasons(
            sacco_id=sacco_id,
            status=status,
            crop_type=crop_type,
            offset=offset,
            limit=limit,
        )
        return [SeasonRead.model_validate(s) for s in seasons]

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------

    def activate_season(self, season_id: uuid.UUID, current_user: User) -> SeasonRead:
        """PLANNED → ACTIVE"""
        return self._transition(season_id, SeasonStatusEnum.active, current_user)

    def harvest_season(self, season_id: uuid.UUID, current_user: User) -> SeasonRead:
        """ACTIVE → HARVESTED"""
        return self._transition(season_id, SeasonStatusEnum.harvested, current_user)

    def fail_season(self, season_id: uuid.UUID, current_user: User) -> SeasonRead:
        """ACTIVE → FAILED"""
        return self._transition(season_id, SeasonStatusEnum.failed, current_user)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _transition(self, season_id: uuid.UUID, target: SeasonStatusEnum, current_user: User) -> SeasonRead:
        season = self.repo.get_season(season_id)
        if season is None:
            raise NotFoundError(f"Season '{season_id}' not found.")

        if current_user.role != RoleEnum.admin and current_user.sacco_id != season.farm.farmer.sacco_id:
            raise ForbiddenError("You can only modify seasons in your own SACCO.")

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
