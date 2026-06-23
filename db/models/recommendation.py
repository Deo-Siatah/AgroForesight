import uuid
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.types import Enum as SaEnum

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.base import TimestampMixin


class RecommendationTypeEnum(str, Enum):
    planting = "planting"
    fertilizer = "fertilizer"
    weeding = "weeding"
    pest = "pest"
    harvest = "harvest"
    weather = "weather"
    finance = "finance"


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    season_id = mapped_column(
        ForeignKey("seasons.id")
    )

    recommendation_type = mapped_column(
        SaEnum(RecommendationTypeEnum, native_enum=True),
        nullable=False,
    )

    message = mapped_column(
        Text
    )

    season = relationship(
        "Season",
        back_populates="recommendations",
    )