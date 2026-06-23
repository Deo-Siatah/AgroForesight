from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from db.models.weather_snapshot import WeatherSnapshot


class WeatherRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_snapshot(
        self,
        farm_id,
        weather_data: dict,
    ) -> WeatherSnapshot:
        snapshot = WeatherSnapshot(
            farm_id=farm_id,
            snapshot_date=date.today(),
            rainfall_mm=weather_data.get("rainfall_mm"),
            temperature_c=weather_data.get("temperature_c"),
            humidity_percent=weather_data.get("humidity_percent"),
            wind_speed_kmh=weather_data.get("wind_speed_kmh"),
            source=weather_data.get("source", "open-meteo"),
        )

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def get_latest_snapshot(
        self,
        farm_id,
    ) -> WeatherSnapshot | None:
        query = (
            select(WeatherSnapshot)
            .where(WeatherSnapshot.farm_id == farm_id)
            .order_by(WeatherSnapshot.snapshot_date.desc())
            .limit(1)
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_weather_history(
        self,
        farm_id,
        limit: int = 30,
    ) -> list[WeatherSnapshot]:
        query = (
            select(WeatherSnapshot)
            .where(WeatherSnapshot.farm_id == farm_id)
            .order_by(WeatherSnapshot.snapshot_date.desc())
            .limit(limit)
        )
        result = self.db.execute(query)
        return result.scalars().all()
