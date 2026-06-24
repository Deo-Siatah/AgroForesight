import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.base import TimestampMixin


class Farmer(Base, TimestampMixin):
    __tablename__ = "farmers"
    __table_args__ = (
        UniqueConstraint("phone", name="uq_farmers_phone"),
        UniqueConstraint("national_id", name="uq_farmers_national_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    sacco_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("saccos.id"),
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
    )

    phone: Mapped[str] = mapped_column(
        String(20),
    )

    national_id: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    sacco = relationship(
        "Sacco",
        back_populates="farmers",
    )

    farms = relationship(
        "Farm",
        back_populates="farmer",
    )

    loans = relationship(
        "Loan",
        back_populates="farmer",
    )