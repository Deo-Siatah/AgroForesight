from pydantic import BaseModel
from pydantic import Field


class RecommendationResponse(BaseModel):

    message: str = Field(
        min_length=20,
        max_length=3000,
        description="Farmer facing recommendation"
    )