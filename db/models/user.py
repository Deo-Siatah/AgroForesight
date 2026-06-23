import uuid
from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.types import Enum as SaEnum

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from db.base import Base
from db.base import TimestampMixin


class RoleEnum(str, Enum):
    admin = "admin"
    sacco_admin = "sacco_admin"
    farmer = "farmer"
    extension_officer = "extension_officer"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sacco_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("saccos.id"),
        nullable=True,
    )

    farmer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("farmers.id"),
        nullable=True,
    )

    role: Mapped[RoleEnum] = mapped_column(
        SaEnum(RoleEnum, native_enum=True),
        nullable=False,
    )