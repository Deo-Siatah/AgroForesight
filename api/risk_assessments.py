from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, require_role
from db.models.user import RoleEnum, User
from services.risk_assesment_service import RiskAssessmentService
from schemas.risk_assesment import RiskAssessmentRead
from schemas.risk_analysis import (
    CalculateRiskResponse
)

_guard = require_role(RoleEnum.admin)

router = APIRouter(prefix="/risks-assessments", tags=["Risk Assessments"])


@router.post("", response_model=CalculateRiskResponse, status_code=201)
async def calculate_risk(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> CalculateRiskResponse:
    """Calculate risk for a loan and persist the assessment."""
    result = await RiskAssessmentService(db).calculate_risk(loan_id)
    # result is now a dict with both "risk_assessment" and "analysis"
    return result

@router.get("", response_model=list[RiskAssessmentRead])
def list_risk_assessments(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _current_user: User = Depends(_guard),
) -> list[RiskAssessmentRead]:
    """List all risk assessments."""
    return RiskAssessmentService(db).risk_repo.list_all(offset=offset, limit=limit)


@router.get("/{assessment_id}", response_model=RiskAssessmentRead)
def get_risk_assessment(
    assessment_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: User = Depends(_guard),
) -> RiskAssessmentRead:
    """Fetch a single risk assessment by ID."""
    return RiskAssessmentService(db).risk_repo.get_by_id(assessment_id)
