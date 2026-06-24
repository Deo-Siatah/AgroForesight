from ai.rules.maize_rules import (
    MaizeRulesEngine,
)

from ai.llm.recommendation_generator import (
    RecommendationGenerator,
)

from repositories.recommendation_repository import (
    RecommendationRepository,
)

from ai.weather.weather_repository import (
    WeatherRepository,
)

from models.recommendation import (
    Recommendation_type_enum,
)


class RecommendationService:

    def __init__(
        self,
        weather_repository: WeatherRepository,
        recommendation_repository: RecommendationRepository,
    ):

        self.weather_repository = weather_repository

        self.recommendation_repository = (
            recommendation_repository
        )

        self.rules_engine = (
            MaizeRulesEngine()
        )

        self.generator = (
            RecommendationGenerator()
        )

    async def generate_for_season(
        self,
        season,
    ):

        weather = (
            await self.weather_repository
            .get_latest_snapshot(
                season.farm_id
            )
        )

        if not weather:
            return None

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
        }

        rule_result = (
            self.rules_engine.evaluate(
                weather=weather_data,
                season_status=season.status.value,
            )
        )

        if not rule_result:
            return None

        llm_response = (
            await self.generator
            .generate_message(
                recommendation_data=rule_result
            )
        )

        recommendation = (
            await self.recommendation_repository
            .create(
                season_id=season.id,
                recommendation_type=(
                    Recommendation_type_enum(
                        rule_result[
                            "recommendation_type"
                        ]
                    )
                ),
                message=llm_response.message,
            )
        )

        return recommendation