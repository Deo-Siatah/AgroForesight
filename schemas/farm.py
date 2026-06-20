"""
schemas/farm.py
Input and output schemas for the Farm entity.
Coordinate validation lives here — clean lat/long from day one
is critical for the satellite monitoring layer planned later.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


class FarmCreate(BaseModel):
    farmer_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    county: str = Field(min_length=1, max_length=100)
    acreage: Decimal = Field(gt=0, decimal_places=2)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)

    @field_validator("name", "county", mode="before")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if isinstance(v, str) and not v.strip():
            raise ValueError("must not be blank")
        return v

    @model_validator(mode="after")
    def coordinates_are_kenya(self) -> "FarmCreate":
        """
        Rough bounding box for Kenya:  lat -5 → +5,  lon 34 → 42.
        Keeps obviously wrong coordinates from polluting the satellite layer.
        """
        if not (-5.0 <= self.latitude <= 5.0):
            raise ValueError(f"latitude {self.latitude} is outside Kenya's bounds (-5 to 5)")
        if not (33.5 <= self.longitude <= 42.0):
            raise ValueError(f"longitude {self.longitude} is outside Kenya's bounds (33.5 to 42)")
        return self


class FarmRead(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    name: str
    county: str
    acreage: Decimal
    latitude: float
    longitude: float
    created_at: datetime

    model_config = {"from_attributes": True}
