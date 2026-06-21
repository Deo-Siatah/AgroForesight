"""
schemas/sacco.py
Input and output schemas for the Sacco entity.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SaccoCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    county: str | None = Field(default=None, max_length=100)
    admin_email: str = Field(min_length=1, max_length=255)
    admin_password: str = Field(min_length=1, max_length=255)

    @field_validator("name", mode="before")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        value = v.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("county", mode="before")
    @classmethod
    def county_normalised(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            return v

        value = v.strip()
        return value or None

    @field_validator("admin_email", mode="before")
    @classmethod
    def admin_email_normalised(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        value = v.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("admin_password", mode="before")
    @classmethod
    def admin_password_not_blank(cls, v: str) -> str:
        if not isinstance(v, str):
            return v

        value = v.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class SaccoRead(BaseModel):
    id: uuid.UUID
    name: str
    county: str | None
    created_at: datetime

    model_config = {"from_attributes": True}