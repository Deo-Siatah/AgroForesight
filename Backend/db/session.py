from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings


def _normalise_url(url: str) -> str:
    """
    Neon and most DB tools emit plain ``postgresql://``.
    SQLAlchemy's psycopg3 driver requires the ``postgresql+psycopg://`` scheme.
    Upgrade the scheme here so the .env value doesn't have to be exact.
    """
    prefix, _, rest = url.partition("://")
    if prefix in ("postgres", "postgresql"):
        return f"postgresql+psycopg://{rest}"
    return url


engine = create_engine(
    _normalise_url(settings.DATABASE_URL),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)