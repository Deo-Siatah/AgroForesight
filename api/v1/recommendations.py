"""
api/v1/recommendations.py
Routes:
  GET  /recommendations                      — recent recommendations (all accessible)
  GET  /recommendations/season/{season_id}   — all recs for a season
  POST /recommendations/generate/{season_id} — generate + persist a new recommendation

Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db, require_role
from db.models.user import RoleEnum, User
from schemas.recommendation import GenerateRecommendationResponse, RecommendationRead
from services.recommendation_service import RecommendationService

_guard = require_role(RoleEnum.admin, RoleEnum.sacco_admin)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=list[RecommendationRead])
def list_recent_recommendations(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> list[RecommendationRead]:
    return RecommendationService(db).list_recent_recommendations(
        current_user, offset=offset, limit=limit
    )


@router.get("/season/{season_id}", response_model=list[RecommendationRead])
def list_season_recommendations(
    season_id: uuid.UUID,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> list[RecommendationRead]:
    return RecommendationService(db).list_season_recommendations(
        season_id, current_user, offset=offset, limit=limit
    )


@router.post("/generate/{season_id}", response_model=GenerateRecommendationResponse)
async def generate_recommendation(
    season_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> GenerateRecommendationResponse:
    rec = await RecommendationService(db).generate_for_season(season_id, current_user)
    return GenerateRecommendationResponse(recommendation=rec)
