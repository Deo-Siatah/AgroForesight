"""
api/deps.py
FastAPI dependencies shared across all routes.
"""
from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy session, ensuring it is closed after the request,
    whether the request succeeded or raised an exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Convenience alias used in route signatures: db: DB
DB = Depends(get_db)
