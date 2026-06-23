"""
services/risk_assessment_service.py

Business brain for risk scoring.

Flow:

Loan
 ↓
Season
 ↓
Farm
 ↓
Weather
 ↓
Recommendations
 ↓
Risk Engine
 ↓
Save Assessment
 ↓
Return Result
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from ai.risks.risk_engine import RiskEngine

from db.models.risk_assesment import RiskAssessment

from repository.loan_repository import LoanRepository
from repository.season_repository import SeasonRepository
from repository.farm_repository import FarmRepository
from services.weather_service import WeatherService

from ai.weather.weather_repository import WeatherRepository
from ai.analyst.risk_interpreter import (RiskInterpreter)

from repository.recommendation_repository import (
    RecommendationRepository,
)

from repository.risk_assesment_repository import (
    RiskAssessmentRepository,
)

from services.exceptions import (
    NotFoundError,
)


class RiskAssessmentService:

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

        self.loan_repo = LoanRepository(db)

        self.season_repo = SeasonRepository(db)

        self.farm_repo = FarmRepository(db)

        self.weather_repo = WeatherRepository(db)

        self.recommendation_repo = (
            RecommendationRepository(db)
        )

        self.risk_repo = (
            RiskAssessmentRepository(db)
        )

        self.risk_engine = RiskEngine()
        self.risk_interpreter = RiskInterpreter()

    # ---------------------------------------------------
    # Calculate
    # ---------------------------------------------------

    async def calculate_risk(
        self,
        loan_id: uuid.UUID,
    ):

        # ----------------------------------------
        # Loan
        # ----------------------------------------

        loan = self.loan_repo.get_loan(
            loan_id
        )

        if loan is None:
            raise NotFoundError(
                f"Loan '{loan_id}' not found."
            )

        if loan.season_id is None:
            raise NotFoundError(
                "Loan has no linked season."
            )

        # ----------------------------------------
        # Season
        # ----------------------------------------

        season = self.season_repo.get_season(
            loan.season_id
        )

        if season is None:
            raise NotFoundError(
                "Season not found."
            )

        # ----------------------------------------
        # Farm
        # ----------------------------------------

        farm = self.farm_repo.get_farm(
            season.farm_id
        )

        if farm is None:
            raise NotFoundError(
                "Farm not found."
            )

        # ----------------------------------------
        # Weather
        # ----------------------------------------

  

        weather = (
            self.weather_repo
            .get_latest_snapshot(
                farm.id
            )
        )


        # No snapshot exists yet
        # Fetch fresh weather and save it

        if weather is None:

            weather = WeatherService(
                self.db
            ).update_farm_weather(
                farm
            )


        weather_data = {

            "rainfall_mm": float(
                weather.rainfall_mm or 0
            ),

            "temperature_c": float(
                weather.temperature_c or 0
            ),

            "humidity_percent": float(
                weather.humidity_percent or 0
            ),

            "wind_speed_kmh": float(
                weather.wind_speed_kmh or 0
            ),

            "source": weather.source,
        }

        # ----------------------------------------
        # Recommendations
        # ----------------------------------------

        recommendations = (
            self.recommendation_repo
            .list_season_recommendations(
                season.id
            )
        )

        recommendation_count = len(
            recommendations
        )

        # ----------------------------------------
        # Risk Engine
        # ----------------------------------------

        result = self.risk_engine.evaluate(
            weather=weather_data,
            season_status=season.status.value,
            expected_harvest_date=(
                season.expected_harvest_date
            ),
            loan_amount=float(
                loan.amount
            ),
            county=farm.county,
            recommendation_count=(
                recommendation_count
            ),
        )

        # ----------------------------------------
        # Persist
        # ----------------------------------------

        assessment = RiskAssessment(
            id=uuid.uuid4(),

            loan_id=loan.id,
            season_id=season.id,

            score=result.score,

            risk_level=result.risk_level.value.lower(),

            weather_risk=result.weather_risk,

            season_risk=result.season_risk,

            harvest_risk=result.harvest_risk,

            financial_risk=result.financial_risk,

            farmer_risk=result.farmer_risk,

            action=result.action.value,
        )

        self.risk_repo.create_assessment(
            assessment
        )

        self.db.commit()

        self.db.refresh(
            assessment
        )
        
        analysis = await self.risk_interpreter.interpret(

            risk_assessment=assessment,

            weather=weather,

            season=season,

            loan=loan,

            farm=farm,

            recommendation_count=recommendation_count,
        )

        return {
            "risk_assessment": assessment,
            "analysis": analysis,
        }

    # ---------------------------------------------------
    # Latest
    # ---------------------------------------------------

    def get_latest_risk(
        self,
        loan_id: uuid.UUID,
    ):

        assessment = (
            self.risk_repo
            .get_latest_for_loan(
                loan_id
            )
        )

        if assessment is None:
            raise NotFoundError(
                "No risk assessment found."
            )

        return assessment

    # ---------------------------------------------------
    # History
    # ---------------------------------------------------

    def get_risk_history(
        self,
        loan_id: uuid.UUID,
    ):

        return (
            self.risk_repo
            .list_loan_assessments(
                loan_id
            )
        )