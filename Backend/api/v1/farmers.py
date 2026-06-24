"""
api/v1/farmers.py
Routes: GET /farmers, POST /farmers, GET /farmers/{id}
Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db, require_role
from db.models.user import RoleEnum, User
from schemas.farmer import FarmerCreate, FarmerRead, FarmerProfile
from services.farmer_service import FarmerService

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.get("", response_model=list[FarmerRead])
def list_farmers(
    sacco_id: uuid.UUID | None = Query(default=None),
    search: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin, RoleEnum.sacco_admin)),
) -> list[FarmerRead]:
    return FarmerService(db).list_farmers(
        current_user, sacco_id=sacco_id, search=search, offset=offset, limit=limit
    )


@router.post("", response_model=FarmerRead, status_code=201)
def register_farmer(
    data: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.admin, RoleEnum.sacco_admin)),
) -> FarmerRead:
    return FarmerService(db).register_farmer(data, current_user)


@router.get("/{farmer_id}", response_model=FarmerProfile)
def get_farmer_profile(
    farmer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FarmerProfile:
    return FarmerService(db).get_farmer_profile(farmer_id, current_user)
