"""
tests/conftest.py

Session-scoped fixtures that wire the full test suite against the live server.

Flow every test run follows:
  1. admin logs in (seeded user from api.md)
  2. admin creates a fresh SACCO via POST /api/v1/saccos  → yields sacco_id + sacco_admin token
  3. all tests run against that SACCO
  4. teardown: nothing to clean up on the live DB — each run uses unique random data

No direct DB access. Everything goes through the API.
"""
from __future__ import annotations

import random
import uuid

import httpx
import pytest

BASE = "http://127.0.0.1:8000"

# Seeded admin from api.md
ADMIN_EMAIL = "admin26@gmail.com"
ADMIN_PASSWORD = "admin26"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rnd_phone() -> str:
    return f"+2547{random.randint(10_000_000, 99_999_999)}"


def rnd_nid() -> str:
    return str(random.randint(10_000_000, 99_999_999))


def rnd_email() -> str:
    return f"user-{uuid.uuid4().hex[:10]}@hifadhi.test"


def login(email: str, password: str) -> str:
    """Return a bearer token for the given credentials."""
    r = httpx.post(f"{BASE}/api/v1/auth/login", json={"email": email, "password": password}, timeout=15)
    assert r.status_code == 200, f"Login failed for {email}: {r.text}"
    return r.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Session fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def admin_token() -> str:
    return login(ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture(scope="session")
def admin_client(admin_token) -> httpx.Client:
    """Persistent httpx client authenticated as platform admin."""
    with httpx.Client(base_url=BASE, headers=auth(admin_token), timeout=15) as c:
        yield c


@pytest.fixture(scope="session")
def sacco_data(admin_client) -> dict:
    """
    Create a fresh SACCO via the API (as admin).
    Returns the full SaccoRead payload plus the raw admin credentials
    so we can log in as the sacco_admin.
    """
    admin_email = rnd_email()
    admin_password = "SaccoAdmin!99"
    r = admin_client.post("/api/v1/saccos", json={
        "name": f"TestSACCO-{uuid.uuid4().hex[:6]}",
        "county": "Nakuru",
        "admin_email": admin_email,
        "admin_password": admin_password,
    })
    assert r.status_code == 201, f"SACCO creation failed: {r.text}"
    return {**r.json(), "_admin_email": admin_email, "_admin_password": admin_password}


@pytest.fixture(scope="session")
def sacco_id(sacco_data) -> uuid.UUID:
    return uuid.UUID(sacco_data["id"])


@pytest.fixture(scope="session")
def sacco_admin_token(sacco_data) -> str:
    return login(sacco_data["_admin_email"], sacco_data["_admin_password"])


@pytest.fixture(scope="session")
def sacco_client(sacco_admin_token) -> httpx.Client:
    """Persistent httpx client authenticated as the session SACCO admin."""
    with httpx.Client(base_url=BASE, headers=auth(sacco_admin_token), timeout=15) as c:
        yield c
