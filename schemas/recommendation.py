"""
schemas/recommendation.py

Input and output schemas for AI recommendations.

Validation lives here.


These schema feeds:
- React dashboard
- SACCO visibility dashboard
- WhatsApp agent
- USSD layer
"""

from __future__ import annotations


import uuid

from datetime import datetime

from pydantic import BaseModel



class RecommendationGenerateResponse(
    BaseModel
):

    recommendation_id: uuid.UUID

    season_id: uuid.UUID

    crop_type: str

    risk_level: str

    recommendation_type: str

    title: str

    message: str


    model_config = {
        "from_attributes": True
    }



class RecommendationRead(
    BaseModel
):

    id: uuid.UUID

    season_id: uuid.UUID

    recommendation_type: str

    message: str

    created_at: datetime


    model_config = {
        "from_attributes": True
    }