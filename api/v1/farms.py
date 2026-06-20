"""
api/v1/farms.py
Routes: POST /farms, GET /farms/{id}
Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from api.deps import require_role
from db.models.user import RoleEnum
from schemas.farm import FarmCreate, FarmRead
from services.farm_service import FarmService

router = APIRouter(
    prefix="/farms",
    tags=["Farms"],
    dependencies=[Depends(require_role(RoleEnum.admin, RoleEnum.sacco_admin))],
)


@router.post("", response_model=FarmRead, status_code=201)
def create_farm(
    data: FarmCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> FarmRead:
    return FarmService(db).create_farm(data, current_user)


@router.get("/{farm_id}", response_model=FarmRead)
def get_farm(
    farm_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> FarmRead:
    return FarmService(db).get_farm(farm_id, current_user)
