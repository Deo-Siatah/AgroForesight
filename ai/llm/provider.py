from google import genai

from core.config import settings


class LLMProvider:

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY
        )

    async def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
        )

        return response.text