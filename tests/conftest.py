"""
tests/conftest.py
Shared fixtures for the full integration test suite.
Uses the real Neon DB — tests create data with random IDs and clean up after.
"""
import uuid
import random
import os
import pytest
import httpx
from sqlalchemy import text

from db.session import SessionLocal
from db.models.sacco import Sacco
from db.models.user import User, RoleEnum


BASE_API_URL = os.getenv("AGROFORESIGHT_API_BASE_URL", "http://127.0.0.1:8000")
ADMIN_EMAIL = "admin26@gmail.com"
ADMIN_PASSWORD = "admin26"
SACCO_ADMIN_EMAIL = "saccoadmin26@gmail.com"
SACCO_ADMIN_PASSWORD = "saccoadmin26"


def login_token(email: str, password: str) -> str:
    with httpx.Client(base_url=BASE_API_URL, timeout=30.0) as c:
        response = c.post("/api/v1/auth/login", json={"email": email, "password": password})
        response.raise_for_status()
        return response.json()["access_token"]


def rnd_phone() -> str:
    return f"+2547{random.randint(10_000_000, 99_999_999)}"


def rnd_nid() -> str:
    return str(random.randint(10_000_000, 99_999_999))


def admin_auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {login_token(ADMIN_EMAIL, ADMIN_PASSWORD)}",
    }


def sacco_admin_auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {login_token(SACCO_ADMIN_EMAIL, SACCO_ADMIN_PASSWORD)}",
    }


# ---------------------------------------------------------------------------
# Client — session-scoped (one per pytest run)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def client(seed_sacco):
    token = login_token(SACCO_ADMIN_EMAIL, SACCO_ADMIN_PASSWORD)
    with httpx.Client(
        base_url=BASE_API_URL,
        timeout=30.0,
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
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
    if test_db.query(User).filter(User.email == ADMIN_EMAIL).first() is None:
        test_db.add(User(
            id=uuid.uuid4(),
            email=ADMIN_EMAIL,
            password_hash=ADMIN_PASSWORD,
            role=RoleEnum.admin,
        ))

    if test_db.query(User).filter(User.email == SACCO_ADMIN_EMAIL).first() is None:
        test_db.add(User(
            id=uuid.uuid4(),
            email=SACCO_ADMIN_EMAIL,
            password_hash=SACCO_ADMIN_PASSWORD,
            role=RoleEnum.sacco_admin,
        ))

    sacco = Sacco(id=uuid.uuid4(), name="AgroTest SACCO", county="Nakuru")
    test_db.add(sacco)
    test_db.flush()

    sacco_admin = test_db.query(User).filter(User.email == SACCO_ADMIN_EMAIL).first()
    if sacco_admin is not None:
        sacco_admin.sacco_id = sacco.id

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
                "DELETE FROM users WHERE farmer_id IN "
                "(SELECT id FROM farmers WHERE sacco_id = :sid)"
            ), {"sid": sid})
            cleanup.execute(text(
                "DELETE FROM users WHERE sacco_id = :sid"
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
