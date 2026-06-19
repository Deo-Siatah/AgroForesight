"""
tests/conftest.py
Shared fixtures for the full integration test suite.
Uses the real Neon DB — tests create data with random IDs and clean up after.
"""
import uuid
import random
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from main import app
from db.session import SessionLocal
from db.models.sacco import Sacco


def rnd_phone() -> str:
    return f"+2547{random.randint(10_000_000, 99_999_999)}"


def rnd_nid() -> str:
    return str(random.randint(10_000_000, 99_999_999))


# ---------------------------------------------------------------------------
# Client — session-scoped (one per pytest run)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# DB session — session-scoped
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_db():
    session = SessionLocal()
    yield session
    session.close()


# ---------------------------------------------------------------------------
# Seed SACCO — session-scoped, cleaned up at the very end
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def seed_sacco(test_db):
    sacco = Sacco(id=uuid.uuid4(), name="AgroTest SACCO", county="Nakuru")
    test_db.add(sacco)
    test_db.commit()

    yield sacco

    # Use a FRESH session for cleanup — the test_db connection may have been
    # terminated by Neon's idle-in-transaction timeout after the long test run.
    cleanup = SessionLocal()
    try:
        sid = str(sacco.id)
        cleanup.execute(text(
            "DELETE FROM loans WHERE farmer_id IN "
            "(SELECT id FROM farmers WHERE sacco_id = :sid)"
        ), {"sid": sid})
        cleanup.execute(text(
            "DELETE FROM recommendations WHERE season_id IN ("
            "  SELECT s.id FROM seasons s"
            "  JOIN farms f ON s.farm_id = f.id"
            "  JOIN farmers fa ON f.farmer_id = fa.id"
            "  WHERE fa.sacco_id = :sid"
            ")"
        ), {"sid": sid})
        cleanup.execute(text(
            "DELETE FROM seasons WHERE farm_id IN ("
            "  SELECT f.id FROM farms f"
            "  JOIN farmers fa ON f.farmer_id = fa.id"
            "  WHERE fa.sacco_id = :sid"
            ")"
        ), {"sid": sid})
        cleanup.execute(text(
            "DELETE FROM farms WHERE farmer_id IN "
            "(SELECT id FROM farmers WHERE sacco_id = :sid)"
        ), {"sid": sid})
        cleanup.execute(text("DELETE FROM farmers WHERE sacco_id = :sid"), {"sid": sid})
        cleanup.execute(text("DELETE FROM saccos WHERE id = :sid"), {"sid": sid})
        cleanup.commit()
    finally:
        cleanup.close()


# ---------------------------------------------------------------------------
# Convenience: expose the sacco UUID for tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sacco_id(seed_sacco) -> uuid.UUID:
    return seed_sacco.id
