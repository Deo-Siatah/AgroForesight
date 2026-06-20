"""
api/v1/seasons.py
Routes:
  POST   /seasons
  GET    /seasons/{id}
  PATCH  /seasons/{id}/activate
  PATCH  /seasons/{id}/harvest
  PATCH  /seasons/{id}/fail

Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from api.deps import require_role
from db.models.user import RoleEnum
from schemas.season import SeasonCreate, SeasonRead
from services.season_service import SeasonService

router = APIRouter(
    prefix="/seasons",
    tags=["Seasons"],
    dependencies=[Depends(require_role(RoleEnum.admin, RoleEnum.sacco_admin))],
)


@router.post("", response_model=SeasonRead, status_code=201)
def create_season(
    data: SeasonCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SeasonRead:
    return SeasonService(db).create_season(data, current_user)


@router.get("/{season_id}", response_model=SeasonRead)
def get_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SeasonRead:
    return SeasonService(db).get_season(season_id, current_user)


@router.patch("/{season_id}/activate", response_model=SeasonRead)
def activate_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SeasonRead:
    return SeasonService(db).activate_season(season_id, current_user)


@router.patch("/{season_id}/harvest", response_model=SeasonRead)
def harvest_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SeasonRead:
    return SeasonService(db).harvest_season(season_id, current_user)


@router.patch("/{season_id}/fail", response_model=SeasonRead)
def fail_season(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> SeasonRead:
    return SeasonService(db).fail_season(season_id, current_user)
