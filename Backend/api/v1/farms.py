"""
api/v1/farms.py
Routes: POST /farms, GET /farms/{id}
Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db, require_role
from db.models.user import RoleEnum, User
from schemas.farm import FarmCreate, FarmRead
from services.farm_service import FarmService

_guard = require_role(RoleEnum.admin, RoleEnum.sacco_admin)

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("", response_model=FarmRead, status_code=201)
def create_farm(
    data: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> FarmRead:
    return FarmService(db).create_farm(data, current_user)


@router.get("/{farm_id}", response_model=FarmRead)
def get_farm(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> FarmRead:
    return FarmService(db).get_farm(farm_id, current_user)
