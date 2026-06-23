import asyncio
import uuid

from db.session import SessionLocal

from repository.season_repository import SeasonRepository
from repository.farm_repository import FarmRepository

from ai.weather.weather_client import WeatherClient


SEASON_ID = uuid.UUID(
    "fda9c39c-0df9-4991-bbfd-43a9c07623dc"
)


async def main():

    db = SessionLocal()

    try:

        season_repo = SeasonRepository(db)
        farm_repo = FarmRepository(db)

        season = season_repo.get_season(SEASON_ID)

        print("\nSeason")
        print(season.id)

        farm = farm_repo.get_farm(season.farm_id)

        print("\nFarm")
        print(farm.id)
        print(farm.latitude)
        print(farm.longitude)

        weather_client = WeatherClient()

        weather = await weather_client.get_weather(
            latitude=float(farm.latitude),
            longitude=float(farm.longitude),
        )

        print("\nWeather")
        print(weather)

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())