from pydantic import BaseModel
from pydantic import Field


class RiskAnalysisResponse(BaseModel):

    summary: str = Field(
        min_length=10,
        max_length=1000,
        description="Short risk summary"
    )

    explanation: str = Field(
        min_length=20,
        max_length=3000,
        description="Detailed explanation of risk score"
    )

    recommendation: str = Field(
        min_length=10,
        max_length=1000,
        description="Recommended intervention"
    )
    key_drivers: list[str] = Field(
        default=[],
        description="List of key drivers contributing to the risk score"
    )