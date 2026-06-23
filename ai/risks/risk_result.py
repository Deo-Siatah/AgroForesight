from dataclasses import dataclass

from ai.risks.intervention_rules import (
    RiskLevel,
    InterventionAction,
)


@dataclass
class RiskResult:

    score: int

    risk_level: RiskLevel

    action: InterventionAction

    weather_risk: int

    season_risk: int

    harvest_risk: int

    financial_risk: int

    farmer_risk: int

    needs_intervention: bool