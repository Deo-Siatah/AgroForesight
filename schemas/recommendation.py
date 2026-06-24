"""
schemas/recommendation.py
Input and output schemas for the Recommendation entity.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from db.models.recommendation import RecommendationTypeEnum


class RecommendationRead(BaseModel):
    id: uuid.UUID
    season_id: uuid.UUID
    recommendation_type: RecommendationTypeEnum
    message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateRecommendationResponse(BaseModel):
    recommendation: RecommendationRead
