"""
api/v1/farmers.py
Routes: POST /farmers, GET /farmers/{id}, GET /farmers/{id}/farms
Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from schemas.farmer import FarmerCreate, FarmerRead, FarmerProfile
from services.farmer_service import FarmerService

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.post("", response_model=FarmerRead, status_code=201)
def register_farmer(data: FarmerCreate, db: Session = Depends(get_db)) -> FarmerRead:
    return FarmerService(db).register_farmer(data)


@router.get("/{farmer_id}", response_model=FarmerProfile)
def get_farmer_profile(farmer_id: uuid.UUID, db: Session = Depends(get_db)) -> FarmerProfile:
    return FarmerService(db).get_farmer_profile(farmer_id)
