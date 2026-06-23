from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InterventionAction(str, Enum):
    MONITOR = "MONITOR"

    CALL_FARMER = "CALL_FARMER"

    EXTENSION_VISIT = "EXTENSION_VISIT"


def determine_risk_level(
    score: int,
) -> RiskLevel:

    if score <= 30:
        return RiskLevel.LOW

    if score <= 60:
        return RiskLevel.MEDIUM

    return RiskLevel.HIGH


def determine_action(
    score: int,
) -> InterventionAction:

    if score <= 30:
        return InterventionAction.MONITOR

    if score <= 60:
        return InterventionAction.CALL_FARMER

    return InterventionAction.EXTENSION_VISIT