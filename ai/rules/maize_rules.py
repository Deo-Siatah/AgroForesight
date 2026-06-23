from enum import Enum
from datetime import date


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendationType(str, Enum):
    PLANTING = "planting"
    FERTILIZER = "fertilizer"
    PEST = "pest"
    WEATHER = "weather"
    HARVEST = "harvest"


class MaizeRulesEngine:

    def evaluate(
        self,
        weather: dict,
        season_status: str,
        days_since_planting: int | None = None,
    ) -> dict:

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

        status = season_status.lower()

        # ----------------------------------
        # PRE-PLANTING
        # ----------------------------------

        if status == "planned":

            if rainfall >= 10 and temperature >= 18:

                return {
                    "risk_level": RiskLevel.LOW,
                    "recommendation_type": RecommendationType.PLANTING,
                    "title": "Suitable Planting Conditions",
                    "message": (
                        "Weather conditions are suitable "
                        "for maize planting. Begin land "
                        "preparation and planting."
                    ),
                }

            return {
                "risk_level": RiskLevel.MEDIUM,
                "recommendation_type": RecommendationType.WEATHER,
                "title": "Delay Planting",
                "message": (
                    "Moisture conditions are currently "
                    "insufficient for planting."
                ),
            }

        # ----------------------------------
        # ACTIVE SEASON
        # ----------------------------------

        if status == "active":

            # Early stage
            if days_since_planting is not None:

                if 0 <= days_since_planting <= 21:

                    return {
                        "risk_level": RiskLevel.LOW,
                        "recommendation_type": RecommendationType.WEATHER,
                        "title": "Monitor Germination",
                        "message": (
                            "Inspect crop establishment "
                            "and replace missing plants."
                        ),
                    }

                if 22 <= days_since_planting <= 45:

                    if rainfall < 20:

                        return {
                            "risk_level": RiskLevel.LOW,
                            "recommendation_type": RecommendationType.FERTILIZER,
                            "title": "Apply Top Dressing",
                            "message": (
                                "Rainfall levels are suitable "
                                "for fertilizer application."
                            ),
                        }

                    return {
                        "risk_level": RiskLevel.HIGH,
                        "recommendation_type": RecommendationType.WEATHER,
                        "title": "Delay Fertilizer Application",
                        "message": (
                            "Rainfall levels may lead to "
                            "fertilizer nutrient loss."
                        ),
                    }

                if 46 <= days_since_planting <= 90:

                    if humidity > 75:

                        return {
                            "risk_level": RiskLevel.MEDIUM,
                            "recommendation_type": RecommendationType.PEST,
                            "title": "Increased Disease Risk",
                            "message": (
                                "High humidity may encourage "
                                "fungal diseases and pests."
                            ),
                        }

                    return {
                        "risk_level": RiskLevel.LOW,
                        "recommendation_type": RecommendationType.WEATHER,
                        "title": "Crop Development Normal",
                        "message": (
                            "Continue monitoring crop growth."
                        ),
                    }

            # General weather warnings

            if temperature > 35:

                return {
                    "risk_level": RiskLevel.HIGH,
                    "recommendation_type": RecommendationType.WEATHER,
                    "title": "Heat Stress Risk",
                    "message": (
                        "High temperatures may reduce yield."
                    ),
                }

        # ----------------------------------
        # HARVESTED
        # ----------------------------------

        if status == "harvested":

            return {
                "risk_level": RiskLevel.LOW,
                "recommendation_type": RecommendationType.HARVEST,
                "title": "Season Complete",
                "message": (
                    "Record yield and prepare for the "
                    "next production cycle."
                ),
            }

        # ----------------------------------
        # DEFAULT
        # ----------------------------------

        return {
            "risk_level": RiskLevel.LOW,
            "recommendation_type": RecommendationType.WEATHER,
            "title": "Conditions Stable",
            "message": (
                "No significant risks detected."
            ),
        }