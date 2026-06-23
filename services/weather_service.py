from sqlalchemy.orm import Session
import asyncio

from ai.weather.weather_client import WeatherClient
from ai.weather.weather_repository import WeatherRepository


class WeatherService:
    def __init__(self, db: Session):
        self.db = db
        self.client = WeatherClient()
        self.repo = WeatherRepository(db)

    def update_farm_weather(self, farm):
        # 1. Get coordinates (run async client synchronously)
        weather = asyncio.run(self.client.get_weather(
            latitude=farm.latitude,
            longitude=farm.longitude,
        ))

        # 2. Save snapshot (sync repo call)
        snapshot = self.repo.create_snapshot(
            farm.id,
            weather
        )

        # Commit after snapshot is added
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot
