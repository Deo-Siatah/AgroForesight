"""
services/loan_service.py
Business brain for the Loan entity.

Valid status transitions (enforced here, never in the repository):
    PENDING   → APPROVED  | REJECTED
    APPROVED  → DISBURSED | REJECTED
    DISBURSED → ACTIVE
    ACTIVE    → REPAID | DEFAULTED

REPAID, DEFAULTED, and REJECTED are terminal — no further transitions allowed.
"""
from __future__ import annotations

import uuid
from typing import Set

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models.loan import Loan, LoanStatusEnum
from repository.loan_repository import LoanRepository
from repository.farmer_repository import FarmerRepository
from schemas.loan import LoanCreate, LoanRead
from services.exceptions import BusinessRuleError, InvalidTransitionError, NotFoundError


# Transition table — the single source of truth for loan status rules.
# Extend here when business requirements change; never touch individual methods.
_TRANSITIONS: dict[LoanStatusEnum, Set[LoanStatusEnum]] = {
    LoanStatusEnum.pending:   {LoanStatusEnum.approved, LoanStatusEnum.rejected},
    LoanStatusEnum.approved:  {LoanStatusEnum.disbursed, LoanStatusEnum.rejected},
    LoanStatusEnum.disbursed: {LoanStatusEnum.active},
    LoanStatusEnum.active:    {LoanStatusEnum.repaid, LoanStatusEnum.defaulted},
    LoanStatusEnum.repaid:    set(),    # terminal
    LoanStatusEnum.defaulted: set(),    # terminal
    LoanStatusEnum.rejected:  set(),    # terminal
}


class LoanService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LoanRepository(db)
        self.farmer_repo = FarmerRepository(db)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_loan(self, data: LoanCreate) -> LoanRead:
        """
        Persist a new loan.
        - Verifies the farmer exists.
        - Amount validation is handled by LoanCreate (> 0).
        - Loan always starts as PENDING — no caller can set status at creation.
        """
        if self.farmer_repo.get_farmer_by_id(data.farmer_id) is None:
            raise NotFoundError(f"Farmer '{data.farmer_id}' not found.")

        loan = Loan(
            id=uuid.uuid4(),
            farmer_id=data.farmer_id,
            amount=data.amount,
            status=LoanStatusEnum.pending,
            risk_score=None,
        )
        self.repo.create_loan(loan)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise BusinessRuleError("Unable to create loan due to conflicting data.") from exc
        self.db.refresh(loan)
        return LoanRead.model_validate(loan)

    def get_loan(self, loan_id: uuid.UUID) -> LoanRead:
        loan = self.repo.get_loan(loan_id)
        if loan is None:
            raise NotFoundError(f"Loan '{loan_id}' not found.")
        return LoanRead.model_validate(loan)

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------

    def approve_loan(self, loan_id: uuid.UUID) -> LoanRead:
        """PENDING → APPROVED"""
        return self._transition(loan_id, LoanStatusEnum.approved)

    def reject_loan(self, loan_id: uuid.UUID) -> LoanRead:
        """PENDING | APPROVED → REJECTED"""
        return self._transition(loan_id, LoanStatusEnum.rejected)

    def disburse_loan(self, loan_id: uuid.UUID) -> LoanRead:
        """APPROVED → DISBURSED"""
        return self._transition(loan_id, LoanStatusEnum.disbursed)

    def activate_loan(self, loan_id: uuid.UUID) -> LoanRead:
        """DISBURSED → ACTIVE"""
        return self._transition(loan_id, LoanStatusEnum.active)

    def repay_loan(self, loan_id: uuid.UUID) -> LoanRead:
        """ACTIVE → REPAID"""
        return self._transition(loan_id, LoanStatusEnum.repaid)

    def default_loan(self, loan_id: uuid.UUID) -> LoanRead:
        """ACTIVE → DEFAULTED"""
        return self._transition(loan_id, LoanStatusEnum.defaulted)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _transition(self, loan_id: uuid.UUID, target: LoanStatusEnum) -> LoanRead:
        loan = self.repo.get_loan(loan_id)
        if loan is None:
            raise NotFoundError(f"Loan '{loan_id}' not found.")

        allowed = _TRANSITIONS.get(loan.status, set())
        if target not in allowed:
            raise InvalidTransitionError(
                f"Cannot move loan from '{loan.status.value}' to '{target.value}'. "
                f"Allowed transitions: {[s.value for s in allowed] or 'none (terminal state)'}."
            )

        self.repo.update_loan_status(loan, target)
        self.db.commit()
        self.db.refresh(loan)
        return LoanRead.model_validate(loan)
