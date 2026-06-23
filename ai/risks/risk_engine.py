from datetime import date

from ai.risks.county_profiles import (
    COUNTY_RISK_MULTIPLIERS,
    DEFAULT_MULTIPLIER,
)

from ai.risks.intervention_rules import (
    determine_action,
    determine_risk_level,
)

from ai.risks.risk_result import RiskResult

from ai.risks.risk_weights import (
    MAX_WEATHER_RISK,
    MAX_SEASON_RISK,
    MAX_HARVEST_RISK,
    MAX_FINANCIAL_RISK,
    MAX_FARMER_RISK,
)


class RiskEngine:

    def evaluate(
        self,
        *,
        weather: dict,
        season_status: str,
        expected_harvest_date,
        loan_amount: float,
        county: str,
        recommendation_count: int,
    ) -> RiskResult:

        weather_risk = self._weather_risk(
            weather,
            county,
        )

        season_risk = self._season_risk(
            season_status,
        )

        harvest_risk = self._harvest_risk(
            expected_harvest_date,
        )

        financial_risk = self._financial_risk(
            loan_amount,
        )

        farmer_risk = self._farmer_risk(
            recommendation_count,
        )

        total_score = (
            weather_risk
            + season_risk
            + harvest_risk
            + financial_risk
            + farmer_risk
        )

        total_score = min(
            total_score,
            100,
        )

        level = determine_risk_level(
            total_score,
        )

        action = determine_action(
            total_score,
        )

        return RiskResult(
            score=total_score,
            risk_level=level,
            action=action,
            weather_risk=weather_risk,
            season_risk=season_risk,
            harvest_risk=harvest_risk,
            financial_risk=financial_risk,
            farmer_risk=farmer_risk,
            needs_intervention=(
                total_score > 60
            ),
        )

    # ----------------------------------------
    # WEATHER
    # ----------------------------------------

    def _weather_risk(
        self,
        weather: dict,
        county: str,
    ) -> int:

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

        risk = 0

        if rainfall < 5:
            risk += 25

        elif rainfall < 15:
            risk += 15

        elif rainfall < 30:
            risk += 8

        if temperature > 38:
            risk += 10

        elif temperature > 34:
            risk += 5

        if humidity > 90:
            risk += 5

        multiplier = COUNTY_RISK_MULTIPLIERS.get(
            county,
            DEFAULT_MULTIPLIER,
        )

        risk = int(
            risk * multiplier
        )

        return min(
            risk,
            MAX_WEATHER_RISK,
        )

    # ----------------------------------------
    # SEASON
    # ----------------------------------------

    def _season_risk(
        self,
        season_status: str,
    ) -> int:

        season_status = season_status.lower()

        if season_status == "failed":
            return MAX_SEASON_RISK

        if season_status == "active":
            return 5

        return 0

    # ----------------------------------------
    # HARVEST
    # ----------------------------------------

    def _harvest_risk(
        self,
        expected_harvest_date,
    ) -> int:

        days_remaining = (
            expected_harvest_date
            - date.today()
        ).days

        if days_remaining <= 14:
            return 20

        if days_remaining <= 30:
            return 15

        if days_remaining <= 60:
            return 8

        return 0

    # ----------------------------------------
    # FINANCIAL
    # ----------------------------------------

    def _financial_risk(
        self,
        loan_amount: float,
    ) -> int:

        if loan_amount >= 250000:
            return 20

        if loan_amount >= 100000:
            return 10

        if loan_amount >= 50000:
            return 5

        return 2

    # ----------------------------------------
    # FARMER
    # ----------------------------------------

    def _farmer_risk(
        self,
        recommendation_count: int,
    ) -> int:

        if recommendation_count == 0:
            return 10

        if recommendation_count <= 2:
            return 5

        return 0