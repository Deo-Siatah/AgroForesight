"""
Repository layer — Recommendation
Responsibility: DB access ONLY.
Recommendation generation logic lives in the Recommendation Service, NOT here.
"""
from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from db.models.recommendation import Recommendation, RecommendationTypeEnum


class RecommendationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Insert a new Recommendation row. Caller is responsible for generation logic."""
        self.db.add(recommendation)
        self.db.flush()
        return recommendation

    # ------------------------------------------------------------------
    # Read — single record
    # ------------------------------------------------------------------

    def get_recommendation(self, recommendation_id: uuid.UUID) -> Recommendation | None:
        return self.db.get(Recommendation, recommendation_id)

    # ------------------------------------------------------------------
    # Read — collections
    # ------------------------------------------------------------------

    def list_season_recommendations(
        self,
        season_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Recommendation]:
        """Return paginated recommendations for a given season."""
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.season_id == season_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
