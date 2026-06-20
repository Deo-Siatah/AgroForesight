"""
tests/test_farmers.py

POST /api/v1/farmers     — admin or owning sacco_admin
GET  /api/v1/farmers/{id} — admin, owning sacco_admin, or the farmer themselves
"""
from __future__ import annotations

import uuid

import httpx

from tests.conftest import rnd_email, rnd_nid, rnd_phone

BASE = "/api/v1/farmers"


def _payload(sacco_id: uuid.UUID, **overrides) -> dict:
    return {
        "sacco_id": str(sacco_id),
        "first_name": "Jane",
        "last_name": "Wanjiku",
        "phone": rnd_phone(),
        "national_id": rnd_nid(),
        "login_email": rnd_email(),
        "login_password": "Farmer!Pass1",
        **overrides,
    }


def create_farmer(client: httpx.Client, sacco_id: uuid.UUID, **overrides) -> dict:
    r = client.post(BASE, json=_payload(sacco_id, **overrides))
    assert r.status_code == 201, f"Farmer creation failed: {r.text}"
    return r.json()


# ---------------------------------------------------------------------------
# POST /api/v1/farmers
# ---------------------------------------------------------------------------

class TestRegisterFarmer:
    def test_sacco_admin_creates_farmer_201(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id))
        assert r.status_code == 201
        body = r.json()
        assert body["first_name"] == "Jane"
        assert body["sacco_id"] == str(sacco_id)
        assert "id" in body
        assert "created_at" in body

    def test_admin_creates_farmer_201(self, admin_client, sacco_id):
        r = admin_client.post(BASE, json=_payload(sacco_id))
        assert r.status_code == 201

    def test_unauthenticated_returns_401(self, sacco_id):
        r = httpx.post("http://127.0.0.1:8000" + BASE, json=_payload(sacco_id), timeout=10)
        assert r.status_code == 401

    def test_sacco_admin_cannot_register_for_other_sacco_403(self, sacco_client):
        other_sacco_id = uuid.uuid4()
        r = sacco_client.post(BASE, json=_payload(other_sacco_id))
        # 403 (forbidden) or 404 (sacco not found) are both acceptable
        assert r.status_code in (403, 404)

    def test_duplicate_phone_returns_409(self, sacco_client, sacco_id):
        phone = rnd_phone()
        sacco_client.post(BASE, json=_payload(sacco_id, phone=phone))
        r = sacco_client.post(BASE, json=_payload(sacco_id, phone=phone))
        assert r.status_code == 409
        assert "phone" in r.json()["detail"].lower()

    def test_duplicate_national_id_returns_409(self, sacco_client, sacco_id):
        nid = rnd_nid()
        sacco_client.post(BASE, json=_payload(sacco_id, national_id=nid))
        r = sacco_client.post(BASE, json=_payload(sacco_id, national_id=nid))
        assert r.status_code == 409
        assert "national" in r.json()["detail"].lower()

    def test_duplicate_login_email_returns_409(self, sacco_client, sacco_id):
        email = rnd_email()
        sacco_client.post(BASE, json=_payload(sacco_id, login_email=email))
        r = sacco_client.post(BASE, json=_payload(sacco_id, login_email=email))
        assert r.status_code == 409

    def test_nonexistent_sacco_returns_404(self, sacco_client):
        # sacco_admin for a real sacco tries a made-up sacco — service checks existence
        r = sacco_client.post(BASE, json=_payload(uuid.uuid4()))
        assert r.status_code in (403, 404)

    def test_blank_first_name_returns_422(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, first_name="   "))
        assert r.status_code == 422

    def test_empty_first_name_returns_422(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, first_name=""))
        assert r.status_code == 422

    def test_blank_last_name_returns_422(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, last_name="   "))
        assert r.status_code == 422

    def test_invalid_phone_format_returns_422(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, phone="not-a-phone"))
        assert r.status_code == 422

    def test_all_zeros_phone_returns_422(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, phone="000000000"))
        assert r.status_code == 422

    def test_plus_zeros_phone_returns_422(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, phone="+000000000"))
        assert r.status_code == 422

    def test_all_zeros_national_id_returns_422(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, national_id="000000000"))
        assert r.status_code == 422

    def test_national_id_is_optional(self, sacco_client, sacco_id):
        r = sacco_client.post(BASE, json=_payload(sacco_id, national_id=None))
        assert r.status_code == 201
        assert r.json()["national_id"] is None

    def test_phone_whitespace_is_stripped(self, sacco_client, sacco_id):
        phone = rnd_phone()
        r = sacco_client.post(BASE, json=_payload(sacco_id, phone=f"  {phone}  "))
        assert r.status_code == 201
        assert r.json()["phone"] == phone

    def test_national_id_whitespace_is_stripped(self, sacco_client, sacco_id):
        nid = rnd_nid()
        r = sacco_client.post(BASE, json=_payload(sacco_id, national_id=f"  {nid}  "))
        assert r.status_code == 201
        assert r.json()["national_id"] == nid

    def test_missing_sacco_id_returns_422(self, sacco_client):
        p = _payload(uuid.uuid4())
        del p["sacco_id"]
        r = sacco_client.post(BASE, json=p)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/farmers/{id}
# ---------------------------------------------------------------------------

class TestGetFarmerProfile:
    def test_sacco_admin_can_read_own_farmer(self, sacco_client, sacco_id):
        farmer = create_farmer(sacco_client, sacco_id)
        r = sacco_client.get(f"{BASE}/{farmer['id']}")
        assert r.status_code == 200
        body = r.json()
        assert body["farmer"]["id"] == farmer["id"]
        assert isinstance(body["farms"], list)
        assert isinstance(body["loans"], list)

    def test_admin_can_read_any_farmer(self, admin_client, sacco_client, sacco_id):
        farmer = create_farmer(sacco_client, sacco_id)
        r = admin_client.get(f"{BASE}/{farmer['id']}")
        assert r.status_code == 200

    def test_farmer_can_read_own_profile(self, sacco_client, sacco_id):
        from tests.conftest import login, auth
        email = rnd_email()
        farmer = create_farmer(sacco_client, sacco_id, login_email=email, login_password="Farmer!Pass1")
        token = login(email, "Farmer!Pass1")
        r = httpx.get(
            f"http://127.0.0.1:8000{BASE}/{farmer['id']}",
            headers=auth(token),
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["farmer"]["id"] == farmer["id"]

    def test_farmer_cannot_read_another_farmers_profile(self, sacco_client, sacco_id):
        from tests.conftest import login, auth
        email_a = rnd_email()
        email_b = rnd_email()
        farmer_a = create_farmer(sacco_client, sacco_id, login_email=email_a, login_password="Pass!1")
        farmer_b = create_farmer(sacco_client, sacco_id, login_email=email_b, login_password="Pass!1")
        token_a = login(email_a, "Pass!1")
        r = httpx.get(
            f"http://127.0.0.1:8000{BASE}/{farmer_b['id']}",
            headers=auth(token_a),
            timeout=10,
        )
        assert r.status_code == 403

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        farmer = create_farmer(sacco_client, sacco_id)
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/{farmer['id']}", timeout=10)
        assert r.status_code == 401

    def test_unknown_farmer_id_returns_404(self, sacco_client):
        r = sacco_client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_invalid_uuid_returns_422(self, sacco_client):
        r = sacco_client.get(f"{BASE}/not-a-uuid")
        assert r.status_code == 422
