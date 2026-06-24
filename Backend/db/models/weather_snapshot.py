from uuid import uuid4
from datetime import date

from sqlalchemy import (
    String,
    Date,
    Numeric,
    ForeignKey,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from db.base import Base
from db.base import TimestampMixin


class WeatherSnapshot(Base, TimestampMixin):
    __tablename__ = "weather_snapshots"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    farm_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farms.id"),
        nullable=False,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    rainfall_mm: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    temperature_c: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    humidity_percent: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    wind_speed_kmh: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        default="open-meteo",
    )

    farm = relationship(
        "Farm",
        back_populates="weather_snapshots",
    )