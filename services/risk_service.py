"""
services/risk_service.py
Strictly isolated risk scoring — plan rule 5.

MVP: simple weighted scoring.
    Failed season     → +40
    Weather alert     → +15  (Phase 1: always 0, weather layer not yet built)
    Missed rec.       → +20  (Phase 1: always 0, recommendation layer not yet built)

Score → Category:
    0–30   Low
    31–60  Medium
    61–100 High

The interface (calculate_risk signature + RiskScore return type) is the
contract that the AI Risk Prediction layer will implement later — without
touching this file, the repository, or any route.
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from db.models.season import SeasonStatusEnum
from repository.loan_repository import LoanRepository
from repository.season_repository import SeasonRepository
from schemas.risk import RiskScore, RiskCategory
from services.exceptions import NotFoundError


class RiskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.loan_repo = LoanRepository(db)
        self.season_repo = SeasonRepository(db)

    def calculate_risk(
        self,
        loan_id: uuid.UUID,
        *,
        season_id: uuid.UUID | None = None,
        # Phase 2 inputs — wired as keyword-only so callers can pass them
        # later without breaking the existing API contract.
        weather_alerts: int = 0,
        missed_recommendations: int = 0,
    ) -> RiskScore:
        """
        Compute a risk score for a loan.

        Phase 1 MVP: only season status contributes to the score.
        Phase 2+: weather_alerts and missed_recommendations will be populated
        by the Weather and Recommendation layers respectively.
        """
        loan = self.loan_repo.get_loan(loan_id)
        if loan is None:
            raise NotFoundError(f"Loan '{loan_id}' not found.")

        score = 0

        # -- Season risk --------------------------------------------------
        if season_id is not None:
            season = self.season_repo.get_season(season_id)
            if season is None:
                raise NotFoundError(f"Season '{season_id}' not found.")
            if season.status == SeasonStatusEnum.failed:
                score += 40

        # -- Weather risk (Phase 2) ---------------------------------------
        score += min(weather_alerts, 1) * 15   # cap: one alert = +15

        # -- Recommendation compliance (Phase 2) --------------------------
        score += min(missed_recommendations, 1) * 20   # cap: one miss = +20

        score = min(score, 100)

        return RiskScore(
            loan_id=loan_id,
            score=score,
            category=self._category(score),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _category(score: int) -> RiskCategory:
        if score <= 30:
            return "low"
        elif score <= 60:
            return "medium"
        return "high"
