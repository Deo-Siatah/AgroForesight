"""
schemas/auth.py
Schemas for login and the authenticated user payload.
"""
from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from db.models.user import RoleEnum


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    role: RoleEnum
    sacco_id: uuid.UUID | None = None
    farmer_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead