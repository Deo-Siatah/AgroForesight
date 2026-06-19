import uuid

from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.base import TimestampMixin


class Sacco(Base, TimestampMixin):
    __tablename__ = "saccos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    county: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    farmers = relationship(
        "Farmer",
        back_populates="sacco",
    )