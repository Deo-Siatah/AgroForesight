"""
api/v1/seasons.py
Routes:
  GET    /seasons
  POST   /seasons
  GET    /seasons/{id}
  PATCH  /seasons/{id}/activate
  PATCH  /seasons/{id}/harvest
  PATCH  /seasons/{id}/fail

Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, require_role
from db.models.user import RoleEnum, User
from db.models.season import SeasonStatusEnum
from schemas.season import SeasonCreate, SeasonRead
from services.season_service import SeasonService

_guard = require_role(RoleEnum.admin, RoleEnum.sacco_admin)

router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("", response_model=list[SeasonRead])
def list_seasons(
    status: SeasonStatusEnum | None = Query(default=None),
    crop_type: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> list[SeasonRead]:
    return SeasonService(db).list_seasons(
        current_user, status=status, crop_type=crop_type, offset=offset, limit=limit
    )


@router.post("", response_model=SeasonRead, status_code=201)
def create_season(
    data: SeasonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> SeasonRead:
    return SeasonService(db).create_season(data, current_user)


@router.get("/{season_id}", response_model=SeasonRead)
def get_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> SeasonRead:
    return SeasonService(db).get_season(season_id, current_user)


@router.patch("/{season_id}/activate", response_model=SeasonRead)
def activate_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> SeasonRead:
    return SeasonService(db).activate_season(season_id, current_user)


@router.patch("/{season_id}/harvest", response_model=SeasonRead)
def harvest_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> SeasonRead:
    return SeasonService(db).harvest_season(season_id, current_user)


@router.patch("/{season_id}/fail", response_model=SeasonRead)
def fail_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> SeasonRead:
    return SeasonService(db).fail_season(season_id, current_user)
