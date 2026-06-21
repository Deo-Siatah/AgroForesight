"""
schemas/risk.py
Output schema for the Risk Service.
Kept separate so the AI Risk Prediction layer can later swap in
without touching Farmer / Loan schemas.
"""
from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel


RiskCategory = Literal["low", "medium", "high"]


class RiskScore(BaseModel):
    loan_id: uuid.UUID
    score: int              # 0–100
    category: RiskCategory  # derived from score
