import uuid
from enum import Enum

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from sqlalchemy.types import Enum as SaEnum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String


from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.base import TimestampMixin


class RiskLevelEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RiskAssessment(Base, TimestampMixin):
    __tablename__ = "risk_assessments"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    loan_id = mapped_column(
        ForeignKey("loans.id"),
        nullable=False,
    )

    season_id = mapped_column(
        ForeignKey("seasons.id"),
        nullable=False,
    )

    score = mapped_column(
        Integer,
        nullable=False,
    )

    risk_level = mapped_column(
        SaEnum(
            RiskLevelEnum,
            native_enum=True,
        ),
        nullable=False,
    )

    weather_risk = mapped_column(
        Integer,
        default=0,
    )

    season_risk = mapped_column(
        Integer,
        default=0,
    )

    harvest_risk = mapped_column(
        Integer,
        default=0,
    )

    report_risk = mapped_column(
        Integer,
        default=0,
    )

    compliance_risk = mapped_column(
        Integer,
        default=0,
    )

    needs_intervention = mapped_column(
        Boolean,
        default=False,
    )
    financial_risk = mapped_column(
    Integer,
    default=0,
    )

    action = mapped_column(String, nullable=True)

    farmer_risk = mapped_column(
        Integer,
        default=0,
    )

    loan = relationship(
        "Loan",
        back_populates="risk_assessments",
    )

    season = relationship(
        "Season",
        back_populates="risk_assessments",
    )

    explanation = mapped_column(
    String,
    nullable=True,
)