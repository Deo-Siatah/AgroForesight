"""
Repository layer — Loan
Responsibility: DB access ONLY.
Status transitions are enforced in the Loan Service, NOT here.
"""
from __future__ import annotations

import uuid
from typing import List

from sqlalchemy.orm import Session

from db.models.loan import Loan, LoanStatusEnum


class LoanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def create_loan(self, loan: Loan) -> Loan:
        """Insert a new Loan row. Caller is responsible for all validation."""
        self.db.add(loan)
        self.db.flush()
        return loan

    def update_loan_status(self, loan: Loan, new_status: LoanStatusEnum) -> Loan:
        """
        Persist a status change on an already-attached Loan instance.
        The Loan Service is responsible for validating the transition before
        calling this method.
        """
        loan.status = new_status
        self.db.flush()
        return loan

    # ------------------------------------------------------------------
    # Read — single record
    # ------------------------------------------------------------------

    def get_loan(self, loan_id: uuid.UUID) -> Loan | None:
        return self.db.get(Loan, loan_id)

    # ------------------------------------------------------------------
    # Read — collections
    # ------------------------------------------------------------------

    def list_loans(
        self,
        *,
        status: LoanStatusEnum | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Loan]:
        """Return a paginated slice of all loans, optionally filtered by status."""
        q = self.db.query(Loan)
        if status is not None:
            q = q.filter(Loan.status == status)
        return q.offset(offset).limit(limit).all()

    def get_farmer_loans(
        self,
        farmer_id: uuid.UUID,
        *,
        status: LoanStatusEnum | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> List[Loan]:
        """Return a paginated list of loans for a specific farmer."""
        q = self.db.query(Loan).filter(Loan.farmer_id == farmer_id)
        if status is not None:
            q = q.filter(Loan.status == status)
        return q.offset(offset).limit(limit).all()
