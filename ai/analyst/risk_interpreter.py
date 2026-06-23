import json
from datetime import date
from pydantic import ValidationError

from ai.analyst.risk_prompt import RiskPrompt
from ai.llm.provider import LLMProvider
from ai.parsers.risk_parser import RiskAnalysisResponse
from services.exceptions import ProcessingError


class RiskInterpreter:

    def __init__(self):
        self.llm = LLMProvider()
        self.prompt_builder = RiskPrompt()

    async def interpret(
        self,
        risk_assessment,
        weather,
        season,
        loan,
        farm,
        recommendation_count,
    ) -> RiskAnalysisResponse:
        """Interpret risk assessment and return structured analysis"""

        payload = {
            # Existing risk engine output
            "score": risk_assessment.score,
            "risk_level": risk_assessment.risk_level,
            "weather_risk": risk_assessment.weather_risk,
            "season_risk": risk_assessment.season_risk,
            "harvest_risk": risk_assessment.harvest_risk,
            "financial_risk": risk_assessment.financial_risk,
            "farmer_risk": risk_assessment.farmer_risk,
            "action": risk_assessment.action,

            # Grounding facts
            "rainfall_mm": float(weather.rainfall_mm or 0),
            "temperature_c": float(weather.temperature_c or 0),
            "humidity_percent": float(weather.humidity_percent or 0),
            "season_status": season.status.value,
            "loan_amount": float(loan.amount),
            "recommendation_count": recommendation_count,
            "expected_harvest_date": str(season.expected_harvest_date),
            "days_to_harvest": (
                season.expected_harvest_date - date.today()
            ).days,
            "county": farm.county,
        }

        prompt = self.prompt_builder.build_prompt(payload)

        # Get response from LLM (should be JSON string)
        response = await self.llm.generate(prompt)

        try:
            # Parse the JSON response
            parsed_data = json.loads(response)
            
            # Handle nested 'analysis' key if present
            if isinstance(parsed_data, dict) and 'analysis' in parsed_data:
                if isinstance(parsed_data['analysis'], str):
                    parsed_data = json.loads(parsed_data['analysis'])
                else:
                    parsed_data = parsed_data['analysis']
            
            # Validate and create Pydantic model
            analysis = RiskAnalysisResponse(**parsed_data)
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Response was: {response[:500]}")
            raise ProcessingError(
                f"LLM returned invalid JSON: {str(e)}"
            )
        except ValidationError as e:
            print(f"❌ Validation Error: {e}")
            print(f"Parsed data: {parsed_data}")
            raise ProcessingError(
                f"LLM response doesn't match schema: {str(e)}"
            )
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            raise ProcessingError(f"Failed to interpret risk: {str(e)}")