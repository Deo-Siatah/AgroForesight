"""
tests/test_saccos.py

POST /api/v1/saccos   — admin only
GET  /api/v1/saccos   — admin only
GET  /api/v1/saccos/{id} — admin only
"""
from __future__ import annotations

import uuid

from tests.conftest import rnd_email

BASE = "/api/v1/saccos"


def _payload(**overrides) -> dict:
    return {
        "name": f"Kilimo SACCO {uuid.uuid4().hex[:4]}",
        "county": "Meru",
        "admin_email": rnd_email(),
        "admin_password": "SecurePass1!",
        **overrides,
    }


# ---------------------------------------------------------------------------
# POST /api/v1/saccos
# ---------------------------------------------------------------------------

class TestCreateSacco:
    def test_admin_creates_sacco_201(self, admin_client):
        r = admin_client.post(BASE, json=_payload())
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert "created_at" in body
        assert body["county"] == "Meru"

    def test_sacco_admin_cannot_create_sacco_403(self, sacco_client):
        r = sacco_client.post(BASE, json=_payload())
        assert r.status_code == 403

    def test_unauthenticated_returns_401(self):
        import httpx
        r = httpx.post(f"http://127.0.0.1:8000{BASE}", json=_payload(), timeout=10)
        assert r.status_code == 401

    def test_duplicate_admin_email_returns_409(self, admin_client):
        email = rnd_email()
        admin_client.post(BASE, json=_payload(admin_email=email))
        r = admin_client.post(BASE, json=_payload(admin_email=email))
        assert r.status_code == 409

    def test_blank_name_returns_422(self, admin_client):
        r = admin_client.post(BASE, json=_payload(name="   "))
        assert r.status_code == 422

    def test_missing_name_returns_422(self, admin_client):
        p = _payload()
        del p["name"]
        r = admin_client.post(BASE, json=p)
        assert r.status_code == 422

    def test_missing_admin_email_returns_422(self, admin_client):
        p = _payload()
        del p["admin_email"]
        r = admin_client.post(BASE, json=p)
        assert r.status_code == 422

    def test_blank_admin_password_returns_422(self, admin_client):
        r = admin_client.post(BASE, json=_payload(admin_password="   "))
        assert r.status_code == 422

    def test_county_is_optional(self, admin_client):
        p = _payload()
        del p["county"]
        r = admin_client.post(BASE, json=p)
        assert r.status_code == 201
        assert r.json()["county"] is None


# ---------------------------------------------------------------------------
# GET /api/v1/saccos
# ---------------------------------------------------------------------------

class TestListSaccos:
    def test_admin_can_list(self, admin_client):
        r = admin_client.get(BASE)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_sacco_admin_cannot_list_403(self, sacco_client):
        r = sacco_client.get(BASE)
        assert r.status_code == 403

    def test_unauthenticated_returns_401(self):
        import httpx
        r = httpx.get(f"http://127.0.0.1:8000{BASE}", timeout=10)
        assert r.status_code == 401

    def test_pagination_offset_and_limit(self, admin_client):
        r = admin_client.get(BASE, params={"offset": 0, "limit": 2})
        assert r.status_code == 200
        assert len(r.json()) <= 2

    def test_invalid_limit_returns_422(self, admin_client):
        r = admin_client.get(BASE, params={"limit": 0})
        assert r.status_code == 422

    def test_negative_offset_returns_422(self, admin_client):
        r = admin_client.get(BASE, params={"offset": -1})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/saccos/{id}
# ---------------------------------------------------------------------------

class TestGetSacco:
    def test_admin_can_fetch_sacco(self, admin_client, sacco_id):
        r = admin_client.get(f"{BASE}/{sacco_id}")
        assert r.status_code == 200
        assert r.json()["id"] == str(sacco_id)

    def test_sacco_admin_cannot_fetch_403(self, sacco_client, sacco_id):
        r = sacco_client.get(f"{BASE}/{sacco_id}")
        assert r.status_code == 403

    def test_unknown_id_returns_404(self, admin_client):
        r = admin_client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_invalid_uuid_returns_422(self, admin_client):
        r = admin_client.get(f"{BASE}/not-a-uuid")
        assert r.status_code == 422
