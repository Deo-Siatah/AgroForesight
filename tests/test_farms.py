"""
tests/test_farms.py

POST /api/v1/farms        — admin or owning sacco_admin
GET  /api/v1/farms/{id}  — admin or owning sacco_admin
"""
from __future__ import annotations

import uuid

import httpx

from tests.conftest import rnd_email, rnd_nid, rnd_phone

FARMERS = "/api/v1/farmers"
BASE = "/api/v1/farms"


def _farmer(client: httpx.Client, sacco_id: uuid.UUID) -> dict:
    r = client.post(FARMERS, json={
        "sacco_id": str(sacco_id),
        "first_name": "Farm",
        "last_name": "Owner",
        "phone": rnd_phone(),
        "national_id": rnd_nid(),
        "login_email": rnd_email(),
        "login_password": "Farmer!Pass1",
    })
    assert r.status_code == 201, r.text
    return r.json()


def _payload(farmer_id: str, **overrides) -> dict:
    return {
        "farmer_id": farmer_id,
        "name": "Wanjiku Maize Farm",
        "county": "Nakuru",
        "acreage": "2.50",
        "latitude": -0.30,
        "longitude": 36.10,
        **overrides,
    }


def create_farm(client: httpx.Client, sacco_id: uuid.UUID, **overrides) -> dict:
    farmer = _farmer(client, sacco_id)
    r = client.post(BASE, json=_payload(farmer["id"], **overrides))
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------------------
# POST /api/v1/farms
# ---------------------------------------------------------------------------

class TestCreateFarm:
    def test_sacco_admin_creates_farm_201(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"]))
        assert r.status_code == 201
        body = r.json()
        assert body["farmer_id"] == farmer["id"]
        assert float(body["acreage"]) == 2.50
        assert "id" in body
        assert "created_at" in body

    def test_admin_creates_farm_201(self, admin_client, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = admin_client.post(BASE, json=_payload(farmer["id"]))
        assert r.status_code == 201

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = httpx.post("http://127.0.0.1:8000" + BASE, json=_payload(farmer["id"]), timeout=10)
        assert r.status_code == 401

    def test_farmer_role_cannot_create_farm_403(self, sacco_client, sacco_id):
        from tests.conftest import login, auth
        email = rnd_email()
        farmer = _farmer(sacco_client, sacco_id)
        # re-create via sacco_client so we have a farmer user
        farmer2 = sacco_client.post(FARMERS, json={
            "sacco_id": str(sacco_id), "first_name": "F", "last_name": "U",
            "phone": rnd_phone(), "national_id": rnd_nid(),
            "login_email": email, "login_password": "Pass!1",
        }).json()
        token = login(email, "Pass!1")
        r = httpx.post(
            "http://127.0.0.1:8000" + BASE,
            json=_payload(farmer2["id"]),
            headers=auth(token),
            timeout=10,
        )
        assert r.status_code == 403

    def test_farmer_not_found_returns_404(self, sacco_client):
        r = sacco_client.post(BASE, json=_payload(str(uuid.uuid4())))
        assert r.status_code == 404

    # --- Kenya bounding-box edge cases ---

    def test_lat_at_northern_boundary_ok(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], latitude=4.9))
        assert r.status_code == 201

    def test_lat_at_southern_boundary_ok(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], latitude=-4.9))
        assert r.status_code == 201

    def test_lat_above_kenya_returns_422(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], latitude=5.1))
        assert r.status_code == 422

    def test_lat_below_kenya_returns_422(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], latitude=-5.1))
        assert r.status_code == 422

    def test_lon_at_eastern_boundary_ok(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], longitude=41.9))
        assert r.status_code == 201

    def test_lon_at_western_boundary_ok(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], longitude=33.6))
        assert r.status_code == 201

    def test_lon_outside_kenya_east_returns_422(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], longitude=42.1))
        assert r.status_code == 422

    def test_lon_outside_kenya_west_returns_422(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], longitude=33.4))
        assert r.status_code == 422

    # --- Acreage edge cases ---

    def test_zero_acreage_returns_422(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], acreage="0"))
        assert r.status_code == 422

    def test_negative_acreage_returns_422(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], acreage="-1.0"))
        assert r.status_code == 422

    def test_very_small_acreage_ok(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], acreage="0.01"))
        assert r.status_code == 201

    def test_blank_name_returns_422(self, sacco_client, sacco_id):
        farmer = _farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_payload(farmer["id"], name="   "))
        assert r.status_code == 422

    def test_missing_farmer_id_returns_422(self, sacco_client):
        p = _payload(str(uuid.uuid4()))
        del p["farmer_id"]
        r = sacco_client.post(BASE, json=p)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/farms/{id}
# ---------------------------------------------------------------------------

class TestGetFarm:
    def test_sacco_admin_can_fetch_farm(self, sacco_client, sacco_id):
        farm = create_farm(sacco_client, sacco_id)
        r = sacco_client.get(f"{BASE}/{farm['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == farm["id"]

    def test_admin_can_fetch_any_farm(self, admin_client, sacco_client, sacco_id):
        farm = create_farm(sacco_client, sacco_id)
        r = admin_client.get(f"{BASE}/{farm['id']}")
        assert r.status_code == 200

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        farm = create_farm(sacco_client, sacco_id)
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/{farm['id']}", timeout=10)
        assert r.status_code == 401

    def test_farmer_cannot_fetch_another_farmers_farm_403(self, sacco_client, sacco_id):
        from tests.conftest import login, auth
        email = rnd_email()
        sacco_client.post(FARMERS, json={
            "sacco_id": str(sacco_id), "first_name": "F", "last_name": "U",
            "phone": rnd_phone(), "national_id": rnd_nid(),
            "login_email": email, "login_password": "Pass!1",
        })
        farm = create_farm(sacco_client, sacco_id)
        token = login(email, "Pass!1")
        r = httpx.get(
            f"http://127.0.0.1:8000{BASE}/{farm['id']}",
            headers=auth(token),
            timeout=10,
        )
        assert r.status_code == 403

    def test_unknown_id_returns_404(self, sacco_client):
        r = sacco_client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_invalid_uuid_returns_422(self, sacco_client):
        r = sacco_client.get(f"{BASE}/not-a-uuid")
        assert r.status_code == 422
