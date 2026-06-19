import uuid
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import Integer
from sqlalchemy.types import Enum as SaEnum

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.base import TimestampMixin


class LoanStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    disbursed = "disbursed"
    active = "active"
    repaid = "repaid"
    defaulted = "defaulted"
    rejected = "rejected"


class Loan(Base, TimestampMixin):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    farmer_id = mapped_column(
        ForeignKey("farmers.id")
    )

    amount = mapped_column(
        Numeric(12, 2)
    )

    status = mapped_column(
        SaEnum(LoanStatusEnum, native_enum=True),
        nullable=False,
    )

    risk_score = mapped_column(Integer)

    farmer = relationship(
        "Farmer",
        back_populates="loans",
    )