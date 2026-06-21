from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendationType(str, Enum):
    PLANTING = "PLANTING"
    FERTILIZER = "FERTILIZER"
    WEATHER_ALERT = "WEATHER_ALERT"


class MaizeRulesEngine:

    def evaluate(
        self,
        weather: dict,
        season_status: str,
    ) -> dict | None:

        rainfall = weather.get(
            "rainfall_mm",
            0,
        )

        temperature = weather.get(
            "temperature_c",
            0,
        )

        humidity = weather.get(
            "humidity_percent",
            0,
        )

        # ---------------------------------
        # PLANTING RULE
        # ---------------------------------

        if (
            season_status == "PLANNING"
            and 20 <= rainfall <= 60
            and temperature >= 18
        ):
            return {
                "risk_level": RiskLevel.LOW,
                "recommendation_type": RecommendationType.PLANTING,
                "title": "Good Planting Window",
                "message": (
                    "Rainfall and temperature conditions "
                    "are favorable for maize planting."
                ),
            }

        # ---------------------------------
        # DROUGHT WARNING
        # ---------------------------------

        if (
            season_status == "PLANNING"
            and rainfall < 10
        ):
            return {
                "risk_level": RiskLevel.HIGH,
                "recommendation_type": RecommendationType.WEATHER_ALERT,
                "title": "Delay Planting",
                "message": (
                    "Rainfall is currently too low. "
                    "Wait for better moisture conditions."
                ),
            }

        # ---------------------------------
        # FERTILIZER RULE
        # ---------------------------------

        if (
            season_status == "GROWING"
            and rainfall < 40
            and humidity > 50
        ):
            return {
                "risk_level": RiskLevel.LOW,
                "recommendation_type": RecommendationType.FERTILIZER,
                "title": "Apply Top Dressing",
                "message": (
                    "Conditions are favorable for "
                    "fertilizer application."
                ),
            }

        # ---------------------------------
        # FERTILIZER WASH-OFF
        # ---------------------------------

        if (
            season_status == "GROWING"
            and rainfall > 70
        ):
            return {
                "risk_level": RiskLevel.HIGH,
                "recommendation_type": RecommendationType.WEATHER_ALERT,
                "title": "Avoid Fertilizer Application",
                "message": (
                    "Heavy rainfall may wash away "
                    "fertilizer nutrients."
                ),
            }

        # ---------------------------------
        # HEAT STRESS
        # ---------------------------------

        if temperature > 35:
            return {
                "risk_level": RiskLevel.HIGH,
                "recommendation_type": RecommendationType.WEATHER_ALERT,
                "title": "Heat Stress Risk",
                "message": (
                    "High temperatures may reduce "
                    "crop performance."
                ),
            }

        return None