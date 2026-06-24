"""
schemas/season.py
Input and output schemas for the Season entity.
Status transitions (PLANNED → ACTIVE → HARVESTED/FAILED) are
enforced in the Season Service, not here.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from db.models.season import SeasonStatusEnum


class SeasonCreate(BaseModel):
    farm_id: uuid.UUID
    crop_type: str = Field(min_length=1, max_length=100)
    planting_date: date
    expected_harvest_date: date

    @model_validator(mode="after")
    def harvest_after_planting(self) -> "SeasonCreate":
        if self.expected_harvest_date <= self.planting_date:
            raise ValueError("expected_harvest_date must be after planting_date")
        return self


class SeasonStatusUpdate(BaseModel):
    """Used by the service to request a specific status transition."""
    status: SeasonStatusEnum


class SeasonRead(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    crop_type: str
    planting_date: date
    expected_harvest_date: date
    status: SeasonStatusEnum
    created_at: datetime

    model_config = {"from_attributes": True}
