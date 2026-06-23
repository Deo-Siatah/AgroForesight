"""
api/v1/loans.py

Routes:
    POST   /loans
    GET    /loans/{loan_id}

    PATCH  /loans/{loan_id}/approve
    PATCH  /loans/{loan_id}/reject
    PATCH  /loans/{loan_id}/disburse
    PATCH  /loans/{loan_id}/activate
    PATCH  /loans/{loan_id}/repay
    PATCH  /loans/{loan_id}/default

    GET    /loans/{loan_id}/risk
    POST   /loans/{loan_id}/risk/recalculate
    GET    /loans/{loan_id}/risk/history

Routes stay thin.
All business logic lives in services.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from api.deps import get_db
from api.deps import require_role

from db.models.user import User
from db.models.user import RoleEnum

from schemas.loan import LoanCreate
from schemas.loan import LoanRead

from schemas.risk_assesment import RiskAssessmentRead


from services.loan_service import LoanService

from services.risk_assesment_service import (
    RiskAssessmentService,
)

_guard = require_role(
    RoleEnum.admin,
    RoleEnum.sacco_admin,
)

router = APIRouter(
    prefix="/loans",
    tags=["Loans"],
)


# ==========================================================
# Create
# ==========================================================

@router.post(
    "",
    response_model=LoanRead,
    status_code=201,
)
def create_loan(
    data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).create_loan(
        data,
        current_user,
    )


# ==========================================================
# Read
# ==========================================================

@router.get(
    "/{loan_id}",
    response_model=LoanRead,
)
def get_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).get_loan(
        loan_id,
        current_user,
    )


# ==========================================================
# Status Transitions
# ==========================================================

@router.patch(
    "/{loan_id}/approve",
    response_model=LoanRead,
)
def approve_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).approve_loan(
        loan_id,
        current_user,
    )


@router.patch(
    "/{loan_id}/reject",
    response_model=LoanRead,
)
def reject_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).reject_loan(
        loan_id,
        current_user,
    )


@router.patch(
    "/{loan_id}/disburse",
    response_model=LoanRead,
)
def disburse_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).disburse_loan(
        loan_id,
        current_user,
    )


@router.patch(
    "/{loan_id}/activate",
    response_model=LoanRead,
)
def activate_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).activate_loan(
        loan_id,
        current_user,
    )


@router.patch(
    "/{loan_id}/repay",
    response_model=LoanRead,
)
def repay_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).repay_loan(
        loan_id,
        current_user,
    )


@router.patch(
    "/{loan_id}/default",
    response_model=LoanRead,
)
def default_loan(
    loan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(_guard),
) -> LoanRead:

    return LoanService(db).default_loan(
        loan_id,
        current_user,
    )


# # ==========================================================
# # Risk Assessment
# # ==========================================================

# @router.get(
#     "/{loan_id}/risk",
#     response_model=RiskAssessmentRead,
# )
# def get_latest_risk(
#     loan_id: uuid.UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(_guard),
# ) -> RiskAssessmentRead:
#     """
#     Return the latest stored risk assessment.

#     Used by:
#         - Loan detail page
#         - SACCO dashboard
#         - AI Analyst
#     """

#     return (
#         RiskAssessmentService(db)
#         .get_latest_risk(
#             loan_id,
#         )
#     )


# @router.post(
#     "/{loan_id}/risk/recalculate",
#     response_model=RiskAnalysisResponse,
# )
# async def recalculate_risk(
#     loan_id: uuid.UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(_guard),
# ) -> RiskAssessmentRead:
#     """
#     Force a new risk calculation.

#     Creates a new RiskAssessment record.
#     """

#     return (
#         await RiskAssessmentService(db)
#         .calculate_risk(
#             loan_id,
#         )
#     )


# @router.get(
#     "/{loan_id}/risk/history",
#     response_model=list[RiskAssessmentRead],
# )
# def get_risk_history(
#     loan_id: uuid.UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(_guard),
# ) -> list[RiskAssessmentRead]:
#     """
#     Return historical risk assessments.

#     Used by:
#         - Trend charts
#         - Portfolio monitoring
#         - AI analyst
#     """

#     return (
#         RiskAssessmentService(db)
#         .get_risk_history(
#             loan_id,
#         )
#     )