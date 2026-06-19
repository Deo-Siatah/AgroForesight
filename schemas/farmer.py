"""
schemas/farmer.py — Farmer schemas + FarmerProfile composite response.

schemas/farmer.py
Input and output schemas for the Farmer entity.
Validation lives here — repositories and ORM models stay dumb.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FarmerCreate(BaseModel):
    sacco_id: uuid.UUID
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    national_id: str | None = Field(default=None, max_length=20)

    @field_validator("phone")
    @classmethod
    def phone_digits_only(cls, v: str) -> str:
        stripped = v.lstrip("+")
        if not stripped.isdigit():
            raise ValueError("phone must contain only digits (and an optional leading +)")
        return v


class FarmerRead(BaseModel):
    id: uuid.UUID
    sacco_id: uuid.UUID
    first_name: str
    last_name: str
    phone: str
    national_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# Imported here to avoid a circular import between farmer ↔ farm/loan schemas.
# FarmerProfile is the canonical shape for get_farmer_profile(); it feeds the
# dashboard, WhatsApp agent, and USSD layer without future schema changes.
from schemas.farm import FarmRead   # noqa: E402
from schemas.loan import LoanRead   # noqa: E402


class FarmerProfile(BaseModel):
    farmer: FarmerRead
    farms: list[FarmRead]
    loans: list[LoanRead]
