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
from db.models.user import RoleEnum, User
from repository.loan_repository import LoanRepository
from repository.farmer_repository import FarmerRepository
from schemas.loan import LoanCreate, LoanRead
from services.exceptions import BusinessRuleError, ForbiddenError, InvalidTransitionError, NotFoundError


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

    def create_loan(self, data: LoanCreate, current_user: User) -> LoanRead:
        """
        Persist a new loan.
        - Verifies the farmer exists.
        - Amount validation is handled by LoanCreate (> 0).
        - Loan always starts as PENDING — no caller can set status at creation.
        """
        farmer = self.farmer_repo.get_farmer_by_id(data.farmer_id)
        if farmer is None:
            raise NotFoundError(f"Farmer '{data.farmer_id}' not found.")

        if current_user.role != RoleEnum.admin and current_user.sacco_id != farmer.sacco_id:
            raise ForbiddenError("You can only create loans for your own SACCO.")

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

    def get_loan(self, loan_id: uuid.UUID, current_user: User) -> LoanRead:
        loan = self.repo.get_loan(loan_id)
        if loan is None:
            raise NotFoundError(f"Loan '{loan_id}' not found.")

        if current_user.role != RoleEnum.admin and current_user.sacco_id != loan.farmer.sacco_id:
            raise ForbiddenError("You can only view loans in your own SACCO.")

        return LoanRead.model_validate(loan)

    def list_loans(
        self,
        current_user: User,
        *,
        farmer_id: uuid.UUID | None = None,
        status: LoanStatusEnum | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[LoanRead]:
        """
        Return a paginated list of loans.
        - admin: can filter by any farmer_id or see all loans.
        - sacco_admin: always scoped to their own SACCO's farmers.
        """
        if farmer_id is not None:
            farmer = self.farmer_repo.get_farmer_by_id(farmer_id)
            if farmer is None:
                raise NotFoundError(f"Farmer '{farmer_id}' not found.")
            if current_user.role != RoleEnum.admin and current_user.sacco_id != farmer.sacco_id:
                raise ForbiddenError("You can only view loans for your own SACCO's farmers.")
            loans = self.repo.get_farmer_loans(
                farmer_id, status=status, offset=offset, limit=limit
            )
        elif current_user.role == RoleEnum.sacco_admin:
            # Scope to all farmers in this SACCO
            from db.models.loan import Loan
            from db.models.farmer import Farmer as FarmerModel
            q = (
                self.repo.db.query(Loan)
                .join(FarmerModel, Loan.farmer_id == FarmerModel.id)
                .filter(FarmerModel.sacco_id == current_user.sacco_id)
            )
            if status is not None:
                q = q.filter(Loan.status == status)
            loans = q.offset(offset).limit(limit).all()
        else:
            loans = self.repo.list_loans(status=status, offset=offset, limit=limit)
        return [LoanRead.model_validate(l) for l in loans]

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------

    def approve_loan(self, loan_id: uuid.UUID, current_user: User) -> LoanRead:
        """PENDING → APPROVED"""
        return self._transition(loan_id, LoanStatusEnum.approved, current_user)

    def reject_loan(self, loan_id: uuid.UUID, current_user: User) -> LoanRead:
        """PENDING | APPROVED → REJECTED"""
        return self._transition(loan_id, LoanStatusEnum.rejected, current_user)

    def disburse_loan(self, loan_id: uuid.UUID, current_user: User) -> LoanRead:
        """APPROVED → DISBURSED"""
        return self._transition(loan_id, LoanStatusEnum.disbursed, current_user)

    def activate_loan(self, loan_id: uuid.UUID, current_user: User) -> LoanRead:
        """DISBURSED → ACTIVE"""
        return self._transition(loan_id, LoanStatusEnum.active, current_user)

    def repay_loan(self, loan_id: uuid.UUID, current_user: User) -> LoanRead:
        """ACTIVE → REPAID"""
        return self._transition(loan_id, LoanStatusEnum.repaid, current_user)

    def default_loan(self, loan_id: uuid.UUID, current_user: User) -> LoanRead:
        """ACTIVE → DEFAULTED"""
        return self._transition(loan_id, LoanStatusEnum.defaulted, current_user)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _transition(self, loan_id: uuid.UUID, target: LoanStatusEnum, current_user: User) -> LoanRead:
        loan = self.repo.get_loan(loan_id)
        if loan is None:
            raise NotFoundError(f"Loan '{loan_id}' not found.")

        if current_user.role != RoleEnum.admin and current_user.sacco_id != loan.farmer.sacco_id:
            raise ForbiddenError("You can only modify loans in your own SACCO.")

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
