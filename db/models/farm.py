import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import Float

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db.base import Base
from db.base import TimestampMixin



class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    farmer_id = mapped_column(
        ForeignKey("farmers.id")
    )

    name = mapped_column(String(255))

    county = mapped_column(String(100))

    acreage = mapped_column(Numeric(10, 2))

    latitude = mapped_column(Float)

    longitude = mapped_column(Float)

    farmer = relationship(
        "Farmer",
        back_populates="farms",
    )

    seasons = relationship(
        "Season",
        back_populates="farm",
    )