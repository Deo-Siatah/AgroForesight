import asyncio
import uuid
from datetime import date

from db.session import SessionLocal

from repository.season_repository import SeasonRepository
from repository.farm_repository import FarmRepository

from ai.weather.weather_client import WeatherClient
from ai.rules.maize_rules import MaizeRulesEngine

from ai.prompts.farmer_prompt import FarmerPrompt
from ai.llm.provider import LLMProvider


SEASON_ID = uuid.UUID(
    "fda9c39c-0df9-4991-bbfd-43a9c07623dc"
)


async def main():

    print("\n" + "=" * 80)
    print("STEP 1: CONNECTING TO DATABASE")
    print("=" * 80)

    db = SessionLocal()

    season_repo = SeasonRepository(db)
    farm_repo = FarmRepository(db)

    print("Database session established")

    # -------------------------------------------------
    # LOAD SEASON
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 2: LOADING SEASON")
    print("=" * 80)

    season = season_repo.get_season(SEASON_ID)

    if not season:
        raise Exception("Season not found")

    print("Season ID:", season.id)
    print("Crop:", season.crop_type)
    print("Status:", season.status)
    print("Planting Date:", season.planting_date)

    # -------------------------------------------------
    # LOAD FARM
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 3: LOADING FARM")
    print("=" * 80)

    farm = farm_repo.get_farm(
        season.farm_id
    )

    if not farm:
        raise Exception("Farm not found")

    print("Farm ID:", farm.id)
    print("Farm Name:", farm.name)
    print("County:", farm.county)
    print("Latitude:", farm.latitude)
    print("Longitude:", farm.longitude)

    # -------------------------------------------------
    # WEATHER
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 4: FETCHING WEATHER")
    print("=" * 80)

    weather_client = WeatherClient()

    weather = await weather_client.get_weather(
        latitude=float(farm.latitude),
        longitude=float(farm.longitude),
    )

    print(weather)

    # -------------------------------------------------
    # CROP AGE
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 5: CALCULATING CROP AGE")
    print("=" * 80)

    days_since_planting = (
        date.today() - season.planting_date
    ).days

    print(
        "Days Since Planting:",
        days_since_planting,
    )

    # -------------------------------------------------
    # RULES ENGINE
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 6: RUNNING RULES ENGINE")
    print("=" * 80)

    rules_engine = MaizeRulesEngine()

    rule_result = rules_engine.evaluate(
        weather=weather,
        season_status=season.status.value,
        days_since_planting=days_since_planting,
    )

    print(rule_result)

    # -------------------------------------------------
    # PROMPT BUILDING
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 7: BUILDING PROMPT")
    print("=" * 80)

    prompt = FarmerPrompt().build_prompt(
        crop_type=season.crop_type,
        county=farm.county,
        recommendation=rule_result,
        weather=weather,
    )

    print(prompt[:1000])

    # -------------------------------------------------
    # GEMINI
    # -------------------------------------------------

    print("\n" + "=" * 80)
    print("STEP 8: CALLING GEMINI")
    print("=" * 80)

    llm = LLMProvider()

    response = await llm.generate(
        prompt
    )

    print(response)

    print("\n" + "=" * 80)
    print("FLOW COMPLETED SUCCESSFULLY")
    print("=" * 80)

    db.close()


if __name__ == "__main__":
    asyncio.run(main())