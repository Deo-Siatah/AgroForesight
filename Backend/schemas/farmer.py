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
    login_email: str = Field(min_length=1, max_length=255)
    login_password: str = Field(min_length=1, max_length=255)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def required_text_not_blank(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        value = v.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("phone", mode="before")
    @classmethod
    def phone_digits_only(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        stripped = v.strip()
        if not stripped:
            raise ValueError("phone must not be blank")

        normalized = stripped.lstrip("+")
        if not normalized.isdigit():
            raise ValueError("phone must contain only digits (and an optional leading +)")
        if set(normalized) == {"0"}:
            raise ValueError("phone cannot be all zeros")
        return stripped

    @field_validator("national_id", mode="before")
    @classmethod
    def national_id_digits_only(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            return v

        value = v.strip()
        if not value:
            raise ValueError("national_id must not be blank")
        if not value.isdigit():
            raise ValueError("national_id must contain only digits")
        if set(value) == {"0"}:
            raise ValueError("national_id cannot be all zeros")
        return value

    @field_validator("login_email", mode="before")
    @classmethod
    def login_email_normalised(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        value = v.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("login_password", mode="before")
    @classmethod
    def login_password_not_blank(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        value = v.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


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
