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

from api.deps import get_db
from schemas.season import SeasonCreate, SeasonRead
from services.season_service import SeasonService

router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.post("", response_model=SeasonRead, status_code=201)
def create_season(data: SeasonCreate, db: Session = Depends(get_db)) -> SeasonRead:
    return SeasonService(db).create_season(data)


@router.get("/{season_id}", response_model=SeasonRead)
def get_season(season_id: uuid.UUID, db: Session = Depends(get_db)) -> SeasonRead:
    return SeasonService(db).get_season(season_id)


@router.patch("/{season_id}/activate", response_model=SeasonRead)
def activate_season(season_id: uuid.UUID, db: Session = Depends(get_db)) -> SeasonRead:
    return SeasonService(db).activate_season(season_id)


@router.patch("/{season_id}/harvest", response_model=SeasonRead)
def harvest_season(season_id: uuid.UUID, db: Session = Depends(get_db)) -> SeasonRead:
    return SeasonService(db).harvest_season(season_id)


@router.patch("/{season_id}/fail", response_model=SeasonRead)
def fail_season(season_id: uuid.UUID, db: Session = Depends(get_db)) -> SeasonRead:
    return SeasonService(db).fail_season(season_id)
