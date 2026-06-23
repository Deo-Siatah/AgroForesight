import asyncio

from ai.llm.recommendation_generator import (
    RecommendationGenerator
)


async def main():

    sample_rule = {
        "recommendation_type": "planting",
        "priority": "high",
        "reason": "Rainfall expected within 5 days",
        "action": "Prepare land and plant maize"
    }

    result = await RecommendationGenerator().generate_message(
        recommendation_data=sample_rule
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())