from pydantic import BaseModel

from schemas.risk_assesment import RiskAssessmentRead

class RiskAnalysisResponse(BaseModel):
    """Analysis portion of risk assessment"""
    summary: str
    explanation: str
    recommendation: str
    key_drivers: list[str] = []


class CalculateRiskResponse(BaseModel):
    """Complete response with both assessment and analysis"""
    risk_assessment: RiskAssessmentRead
    analysis: RiskAnalysisResponse