"""
api/v1/saccos.py
Routes: POST /saccos, GET /saccos, GET /saccos/{id}
Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from api.deps import require_role
from db.models.user import RoleEnum
from schemas.sacco import SaccoCreate, SaccoRead
from services.sacco_service import SaccoService

router = APIRouter(
    prefix="/saccos",
    tags=["Saccos"],
    dependencies=[Depends(require_role(RoleEnum.admin))],
)


@router.post("", response_model=SaccoRead, status_code=201)
def create_sacco(
    data: SaccoCreate,
    db: Session = Depends(get_db),
    _current_user = Depends(require_role(RoleEnum.admin)),
) -> SaccoRead:
    return SaccoService(db).create_sacco(data)


@router.get("", response_model=list[SaccoRead])
def list_saccos(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[SaccoRead]:
    return SaccoService(db).list_saccos(offset=offset, limit=limit)


@router.get("/{sacco_id}", response_model=SaccoRead)
def get_sacco(sacco_id: uuid.UUID, db: Session = Depends(get_db)) -> SaccoRead:
    return SaccoService(db).get_sacco(sacco_id)