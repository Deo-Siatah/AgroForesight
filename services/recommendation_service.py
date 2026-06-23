"""
services/recommendation_service.py

Business brain for AI generated recommendations.

Flow:

Season
    ↓
Farm coordinates
    ↓
Weather Intelligence from meteo api
    ↓
Maize Rules Engine
    ↓
Prompt Builder
    ↓
LLM
    ↓
Recommendation Database

The service coordinates the AI pipeline.
Repositories only handle database operations.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from db.models.user import User, RoleEnum
from db.models.recommendation import (
    Recommendation,
    RecommendationTypeEnum,
)


from repository.season_repository import SeasonRepository
from repository.farm_repository import FarmRepository
from repository.recommendation_repository import (
    RecommendationRepository,
)


from schemas.recommendation import (
    RecommendationGenerateResponse,
)


from services.exceptions import (
    NotFoundError,
    ForbiddenError,
    BusinessRuleError,
)


from ai.weather.weather_client import WeatherClient
from ai.rules.maize_rules import MaizeRulesEngine
from ai.prompts.farmer_prompt import FarmerPrompt
from ai.llm.provider import LLMProvider



class RecommendationService:

    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db


        # Database layer

        self.season_repo = SeasonRepository(db)

        self.farm_repo = FarmRepository(db)

        self.recommendation_repo = (
            RecommendationRepository(db)
        )


        # AI layer

        self.weather_client = WeatherClient()

        self.rules_engine = MaizeRulesEngine()

        self.prompt_builder = FarmerPrompt()

        self.llm = LLMProvider()



    # ---------------------------------------------------------
    # Generate recommendation
    # ---------------------------------------------------------

    async def generate_recommendation(
        self,
        season_id: uuid.UUID,
        current_user: User,
    ) -> RecommendationGenerateResponse:


        # -----------------------------------------------------
        # 1. Get season
        # -----------------------------------------------------

        season = self.season_repo.get_season(
            season_id
        )


        if season is None:

            raise NotFoundError(
                f"Season '{season_id}' not found."
            )



        # -----------------------------------------------------
        # 2. Permission check
        # -----------------------------------------------------

        if (
            current_user.role != RoleEnum.admin
            and current_user.sacco_id
            != season.farm.farmer.sacco_id
        ):

            raise ForbiddenError(
                "You can only generate recommendations "
                "for your own SACCO."
            )



        # -----------------------------------------------------
        # 3. Get farm
        # -----------------------------------------------------

        farm = self.farm_repo.get_farm(
            season.farm_id
        )


        if farm is None:

            raise NotFoundError(
                f"Farm '{season.farm_id}' not found."
            )



        # -----------------------------------------------------
        # 4. Weather intelligence
        # -----------------------------------------------------

        weather = await self.weather_client.get_weather(
            latitude=float(farm.latitude),
            longitude=float(farm.longitude),
        )



        # -----------------------------------------------------
        # 5. Crop age calculation
        # -----------------------------------------------------

        days_since_planting = 0


        if season.planting_date:

            days_since_planting = max(
                0,
                (
                    date.today()
                    -
                    season.planting_date
                ).days,
            )



        # -----------------------------------------------------
        # 6. Rules engine
        # -----------------------------------------------------

        rule_result = self.rules_engine.evaluate(
            weather=weather,
            season_status=season.status.value,
            days_since_planting=
            days_since_planting,
        )



        # fallback if no rule triggers

        if rule_result is None:

            rule_result = {

                "risk_level": "LOW",

                "recommendation_type":
                RecommendationTypeEnum.weather,

                "title":
                "Conditions Stable",

                "message":
                "No immediate risks detected."

            }



        # -----------------------------------------------------
        # 7. Build farmer prompt
        # -----------------------------------------------------

        prompt = (
            self.prompt_builder.build_prompt(
                recommendation=rule_result,
                weather=weather,
                crop_type=season.crop_type,
                county=farm.county,
            )
        )



        # -----------------------------------------------------
        # 8. Generate LLM response
        # -----------------------------------------------------

        llm_message = await self.llm.generate(
            prompt
        )



        # -----------------------------------------------------
        # 9. Convert enum for database
        # -----------------------------------------------------

        recommendation_type = (
            rule_result[
                "recommendation_type"
            ]
        )


        if isinstance(
            recommendation_type,
            str
        ):

            recommendation_type = (
                RecommendationTypeEnum(
                    recommendation_type.lower()
                )
            )



        # -----------------------------------------------------
        # 10. Save recommendation
        # -----------------------------------------------------

        recommendation = Recommendation(

            id=uuid.uuid4(),

            season_id=season.id,

            recommendation_type=
            recommendation_type,

            message=llm_message,

        )



        self.recommendation_repo.create_recommendation(
            recommendation
        )


        try:

            self.db.commit()


        except IntegrityError as exc:

            self.db.rollback()

            raise BusinessRuleError(
                "Failed saving recommendation."
            ) from exc



        self.db.refresh(
            recommendation
        )



        # -----------------------------------------------------
        # 11. Return API response
        # -----------------------------------------------------

        return RecommendationGenerateResponse(

            recommendation_id=
            recommendation.id,


            season_id=
            season.id,


            crop_type=
            season.crop_type,


            risk_level=
            str(
                rule_result["risk_level"]
            ),


            recommendation_type=
            recommendation_type.value,


            title=
            rule_result["title"],


            message=
            llm_message,

        )