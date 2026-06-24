from ai.llm.provider import LLMProvider
from ai.parsers.recommendation_parser import (
    RecommendationResponse,
)
from ai.prompts.farmer_prompt import FarmerPrompt


class RecommendationGenerator:

    def __init__(self):

        self.provider = LLMProvider()
        self.prompt_builder = FarmerPrompt()

    async def generate_message(
        self,
        recommendation_data: dict,
    ) -> RecommendationResponse:

        prompt = self.prompt_builder.build_prompt(
            recommendation_data
        )

        raw_response = await self.provider.generate(
            prompt
        )

        return RecommendationResponse(
            message=raw_response.strip()
        )