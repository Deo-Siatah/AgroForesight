"""
api/v1/recommendations.py

Routes:
POST /recommendations/generate/{season_id}
GET  /recommendations/season/{season_id}

Routes stay thin.
Business logic lives inside RecommendationService.
"""

from __future__ import annotations


import uuid


from fastapi import APIRouter, Depends


from sqlalchemy.orm import Session


from api.deps import (
    get_db,
    require_role,
)


from db.models.user import (
    RoleEnum,
    User,
)


from schemas.recommendation import (
    RecommendationGenerateResponse,
    RecommendationRead,
)


from services.recommendation_service import (
    RecommendationService,
)


from repository.recommendation_repository import (
    RecommendationRepository,
)



_guard = require_role(
    RoleEnum.admin,
    RoleEnum.sacco_admin,
)



router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)



# -----------------------------------------------------
# Generate AI recommendation
# -----------------------------------------------------

@router.post(
    "/generate/{season_id}",
    response_model=RecommendationGenerateResponse,
    status_code=201,
)
async def generate_recommendation(

    season_id: uuid.UUID,

    db: Session = Depends(get_db),

    current_user: User = Depends(_guard),

) -> RecommendationGenerateResponse:


    return await RecommendationService(
        db
    ).generate_recommendation(

        season_id=season_id,

        current_user=current_user,

    )



# -----------------------------------------------------
# Get recommendations for season
# -----------------------------------------------------

@router.get(
    "/season/{season_id}",
    response_model=list[RecommendationRead],
)
def get_season_recommendations(

    season_id: uuid.UUID,

    db: Session = Depends(get_db),

    current_user: User = Depends(_guard),

) -> list[RecommendationRead]:


    repo = RecommendationRepository(
        db
    )


    recommendations = (
        repo.list_season_recommendations(
            season_id
        )
    )


    return recommendations