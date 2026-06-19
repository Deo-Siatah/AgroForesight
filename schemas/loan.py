"""
schemas/loan.py
Input and output schemas for the Loan entity.
Status starts as PENDING — the service drives all transitions.
The valid flow is: Pending → Approved → Disbursed → Active → Repaid / Defaulted.
Blocking invalid transitions (e.g. Repaid → Active) is the Loan Service's job.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from db.models.loan import LoanStatusEnum


class LoanCreate(BaseModel):
    farmer_id: uuid.UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    # season_id is optional at creation but strongly encouraged (see plan rule 9)
    season_id: uuid.UUID | None = None


class LoanRead(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    amount: Decimal
    status: LoanStatusEnum
    risk_score: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
