"""
services/recommendation_service.py
Business brain for the Recommendation entity.

Responsibilities:
  - list_season_recommendations: paginated fetch from DB
  - list_recent_recommendations: most recent N across all accessible seasons
  - generate_for_season: run rules engine + LLM, persist result, return it
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from db.models.recommendation import Recommendation, RecommendationTypeEnum
from db.models.season import Season
from db.models.user import RoleEnum, User
from repository.recommendation_repository import RecommendationRepository
from repository.season_repository import SeasonRepository
from schemas.recommendation import RecommendationRead
from services.exceptions import ForbiddenError, NotFoundError, BusinessRuleError


class RecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RecommendationRepository(db)
        self.season_repo = SeasonRepository(db)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def list_season_recommendations(
        self,
        season_id: uuid.UUID,
        current_user: User,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[RecommendationRead]:
        season = self.season_repo.get_season(season_id)
        if season is None:
            raise NotFoundError(f"Season '{season_id}' not found.")

        self._assert_sacco_access(current_user, season)

        recs = self.repo.list_season_recommendations(season_id, offset=offset, limit=limit)
        return [RecommendationRead.model_validate(r) for r in recs]

    def list_recent_recommendations(
        self,
        current_user: User,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[RecommendationRead]:
        """Return the most recent recommendations, scoped to the caller's SACCO."""
        q = (
            self.db.query(Recommendation)
            .join(Season, Recommendation.season_id == Season.id)
        )
        if current_user.role != RoleEnum.admin:
            from db.models.farm import Farm
            from db.models.farmer import Farmer
            q = (
                q.join(Farm, Season.farm_id == Farm.id)
                .join(Farmer, Farm.farmer_id == Farmer.id)
                .filter(Farmer.sacco_id == current_user.sacco_id)
            )
        recs = q.order_by(Recommendation.created_at.desc()).offset(offset).limit(limit).all()
        return [RecommendationRead.model_validate(r) for r in recs]

    # ------------------------------------------------------------------
    # Generate
    # ------------------------------------------------------------------

    async def generate_for_season(
        self,
        season_id: uuid.UUID,
        current_user: User,
    ) -> RecommendationRead:
        """Run the rules engine + LLM and persist a new Recommendation."""
        season = self.season_repo.get_season(season_id)
        if season is None:
            raise NotFoundError(f"Season '{season_id}' not found.")

        self._assert_sacco_access(current_user, season)

        # Build a minimal rule-data dict from what we know about the season.
        recommendation_data = {
            "recommendation_type": "planting",
            "priority": "medium",
            "reason": f"Season status is '{season.status.value}' for crop '{season.crop_type}'",
            "action": f"Review your {season.crop_type} crop and ensure field conditions are optimal.",
        }

        try:
            from ai.llm.recommendation_generator import RecommendationGenerator
            response = await RecommendationGenerator().generate_message(
                recommendation_data=recommendation_data
            )
            message = response.message
        except Exception as exc:
            raise BusinessRuleError(
                f"LLM generation failed: {exc}. Check that GOOGLE_API_KEY is set and valid."
            ) from exc

        rec = Recommendation(
            id=uuid.uuid4(),
            season_id=season_id,
            recommendation_type=RecommendationTypeEnum.planting,
            message=message,
        )
        self.repo.create_recommendation(rec)
        self.db.commit()
        self.db.refresh(rec)
        return RecommendationRead.model_validate(rec)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _assert_sacco_access(self, current_user: User, season: Season) -> None:
        if current_user.role == RoleEnum.admin:
            return
        if current_user.sacco_id != season.farm.farmer.sacco_id:
            raise ForbiddenError("You can only access recommendations for your own SACCO.")
