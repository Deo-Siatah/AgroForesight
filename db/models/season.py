import uuid

from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from enum import Enum

from db.base import Base
from db.base import TimestampMixin

class SeasonStatusEnum(str, Enum):
    planned = "planned"
    active = "active"
    harvested = "harvested"
    failed = "failed"

class Season(Base, TimestampMixin):
    __tablename__ = "seasons"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    farm_id = mapped_column(
        ForeignKey("farms.id")
    )

    crop_type = mapped_column(String(100))

    planting_date = mapped_column(Date)

    expected_harvest_date = mapped_column(Date)

    status = mapped_column(
        Enum(SeasonStatusEnum, native_enum=True),
        nullable=False,
    )

    farm = relationship(
        "Farm",
        back_populates="seasons",
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="season",
    )