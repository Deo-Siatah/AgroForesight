"""
Repository layer — Risk Assessment

Responsibility:
Database access ONLY.

NO:

"""

from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from db.models.risk_assesment import RiskAssessment


class RiskAssessmentRepository:

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # ---------------------------------------------------
    # Write
    # ---------------------------------------------------

    def create_assessment(
        self,
        assessment: RiskAssessment,
    ) -> RiskAssessment:

        self.db.add(assessment)

        self.db.flush()

        return assessment

    # ---------------------------------------------------
    # Read Single
    # ---------------------------------------------------

    def get_assessment(
        self,
        assessment_id: uuid.UUID,
    ) -> RiskAssessment | None:

        return self.db.get(
            RiskAssessment,
            assessment_id,
        )

    # ---------------------------------------------------
    # Read Latest
    # ---------------------------------------------------

    def get_latest_for_loan(
        self,
        loan_id: uuid.UUID,
    ) -> RiskAssessment | None:

        return (
            self.db.query(RiskAssessment)
            .filter(
                RiskAssessment.loan_id == loan_id
            )
            .order_by(
                RiskAssessment.created_at.desc()
            )
            .first()
        )

    # ---------------------------------------------------
    # History
    # ---------------------------------------------------

    def list_loan_assessments(
        self,
        loan_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> List[RiskAssessment]:

        return (
            self.db.query(RiskAssessment)
            .filter(
                RiskAssessment.loan_id == loan_id
            )
            .order_by(
                RiskAssessment.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )