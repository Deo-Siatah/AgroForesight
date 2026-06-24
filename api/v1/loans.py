"""
api/v1/loans.py
Routes:
  GET    /loans
  POST   /loans
  GET    /loans/{id}
  PATCH  /loans/{id}/approve
  PATCH  /loans/{id}/reject
  PATCH  /loans/{id}/disburse
  PATCH  /loans/{id}/activate
  PATCH  /loans/{id}/repay
  PATCH  /loans/{id}/default
  GET    /loans/{id}/risk
  POST   /loans/{id}/risk/recalculate

Routes stay thin — call a service, return its result.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, require_role
from db.models.user import RoleEnum, User
from db.models.loan import LoanStatusEnum
from schemas.loan import LoanCreate, LoanRead
from schemas.risk import RiskScore
from services.loan_service import LoanService
from services.risk_service import RiskService

_guard = require_role(RoleEnum.admin, RoleEnum.sacco_admin)

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get("", response_model=list[LoanRead])
def list_loans(
    farmer_id: uuid.UUID | None = Query(default=None),
    status: LoanStatusEnum | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> list[LoanRead]:
    return LoanService(db).list_loans(
        current_user, farmer_id=farmer_id, status=status, offset=offset, limit=limit
    )


@router.post("", response_model=LoanRead, status_code=201)
def create_loan(
    data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).create_loan(data, current_user)


@router.get("/{loan_id}", response_model=LoanRead)
def get_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).get_loan(loan_id, current_user)


# --- Status transitions ---------------------------------------------------

@router.patch("/{loan_id}/approve", response_model=LoanRead)
def approve_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).approve_loan(loan_id, current_user)


@router.patch("/{loan_id}/reject", response_model=LoanRead)
def reject_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).reject_loan(loan_id, current_user)


@router.patch("/{loan_id}/disburse", response_model=LoanRead)
def disburse_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).disburse_loan(loan_id, current_user)


@router.patch("/{loan_id}/activate", response_model=LoanRead)
def activate_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).activate_loan(loan_id, current_user)


@router.patch("/{loan_id}/repay", response_model=LoanRead)
def repay_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).repay_loan(loan_id, current_user)


@router.patch("/{loan_id}/default", response_model=LoanRead)
def default_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:
    return LoanService(db).default_loan(loan_id, current_user)


# --- Risk ------------------------------------------------------------------

@router.get("/{loan_id}/risk", response_model=RiskScore)
def get_risk(
    loan_id: uuid.UUID,
    season_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> RiskScore:
    """
    Compute and return the current risk score for a loan.
    Pass ?season_id=<uuid> to factor in season status.
    Powers SACCO officer dashboards.
    """
    return RiskService(db).calculate_risk(loan_id, season_id=season_id, current_user=current_user)


@router.post("/{loan_id}/risk/recalculate", response_model=RiskScore)
def recalculate_risk(
    loan_id: uuid.UUID,
    season_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> RiskScore:
    """Force a fresh risk calculation and return the updated score."""
    return RiskService(db).calculate_risk(loan_id, season_id=season_id, current_user=current_user)
