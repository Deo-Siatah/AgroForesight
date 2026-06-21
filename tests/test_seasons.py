"""
tests/test_seasons.py

POST   /api/v1/seasons
GET    /api/v1/seasons/{id}
PATCH  /api/v1/seasons/{id}/activate
PATCH  /api/v1/seasons/{id}/harvest
PATCH  /api/v1/seasons/{id}/fail
"""
from __future__ import annotations

import uuid

import httpx

from tests.conftest import rnd_email, rnd_nid, rnd_phone

FARMERS = "/api/v1/farmers"
FARMS = "/api/v1/farms"
BASE = "/api/v1/seasons"


def _make_farm(client: httpx.Client, sacco_id: uuid.UUID) -> str:
    farmer = client.post(FARMERS, json={
        "sacco_id": str(sacco_id), "first_name": "S", "last_name": "T",
        "phone": rnd_phone(), "national_id": rnd_nid(),
        "login_email": rnd_email(), "login_password": "Pass!1",
    }).json()
    farm = client.post(FARMS, json={
        "farmer_id": farmer["id"], "name": "Season Test Farm",
        "county": "Nakuru", "acreage": "1.0",
        "latitude": -0.30, "longitude": 36.10,
    }).json()
    return farm["id"]


def _season_payload(farm_id: str, **overrides) -> dict:
    return {
        "farm_id": farm_id,
        "crop_type": "Maize",
        "planting_date": "2025-03-01",
        "expected_harvest_date": "2025-07-01",
        **overrides,
    }


def create_season(client: httpx.Client, sacco_id: uuid.UUID, **overrides) -> dict:
    farm_id = _make_farm(client, sacco_id)
    r = client.post(BASE, json=_season_payload(farm_id, **overrides))
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------------------------------------------------------------
# POST /api/v1/seasons
# ---------------------------------------------------------------------------

class TestCreateSeason:
    def test_sacco_admin_creates_season_201(self, sacco_client, sacco_id):
        farm_id = _make_farm(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_season_payload(farm_id))
        assert r.status_code == 201
        body = r.json()
        assert body["status"] == "planned"
        assert body["crop_type"] == "Maize"
        assert "id" in body
        assert "created_at" in body

    def test_admin_creates_season_201(self, admin_client, sacco_client, sacco_id):
        farm_id = _make_farm(sacco_client, sacco_id)
        r = admin_client.post(BASE, json=_season_payload(farm_id))
        assert r.status_code == 201

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        farm_id = _make_farm(sacco_client, sacco_id)
        r = httpx.post("http://127.0.0.1:8000" + BASE, json=_season_payload(farm_id), timeout=10)
        assert r.status_code == 401

    def test_farm_not_found_returns_404(self, sacco_client):
        r = sacco_client.post(BASE, json=_season_payload(str(uuid.uuid4())))
        assert r.status_code == 404

    def test_harvest_before_planting_returns_422(self, sacco_client, sacco_id):
        farm_id = _make_farm(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_season_payload(
            farm_id, planting_date="2025-07-01", expected_harvest_date="2025-03-01"
        ))
        assert r.status_code == 422

    def test_same_planting_and_harvest_date_returns_422(self, sacco_client, sacco_id):
        farm_id = _make_farm(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_season_payload(
            farm_id, planting_date="2025-03-01", expected_harvest_date="2025-03-01"
        ))
        assert r.status_code == 422

    def test_blank_crop_type_returns_422(self, sacco_client, sacco_id):
        farm_id = _make_farm(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_season_payload(farm_id, crop_type=""))
        assert r.status_code == 422

    def test_invalid_date_format_returns_422(self, sacco_client, sacco_id):
        farm_id = _make_farm(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json=_season_payload(farm_id, planting_date="not-a-date"))
        assert r.status_code == 422

    def test_missing_farm_id_returns_422(self, sacco_client):
        p = _season_payload(str(uuid.uuid4()))
        del p["farm_id"]
        r = sacco_client.post(BASE, json=p)
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/seasons/{id}
# ---------------------------------------------------------------------------

class TestGetSeason:
    def test_fetch_returns_correct_shape(self, sacco_client, sacco_id):
        season = create_season(sacco_client, sacco_id)
        r = sacco_client.get(f"{BASE}/{season['id']}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == season["id"]
        assert body["status"] == "planned"
        assert "farm_id" in body
        assert "planting_date" in body
        assert "expected_harvest_date" in body

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        season = create_season(sacco_client, sacco_id)
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/{season['id']}", timeout=10)
        assert r.status_code == 401

    def test_unknown_id_returns_404(self, sacco_client):
        r = sacco_client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_invalid_uuid_returns_422(self, sacco_client):
        r = sacco_client.get(f"{BASE}/not-a-uuid")
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

class TestSeasonTransitions:
    def test_planned_to_active(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        r = sacco_client.patch(f"{BASE}/{s['id']}/activate")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

    def test_active_to_harvested(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        sacco_client.patch(f"{BASE}/{s['id']}/activate")
        r = sacco_client.patch(f"{BASE}/{s['id']}/harvest")
        assert r.status_code == 200
        assert r.json()["status"] == "harvested"

    def test_active_to_failed(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        sacco_client.patch(f"{BASE}/{s['id']}/activate")
        r = sacco_client.patch(f"{BASE}/{s['id']}/fail")
        assert r.status_code == 200
        assert r.json()["status"] == "failed"

    def test_planned_cannot_harvest_directly(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        r = sacco_client.patch(f"{BASE}/{s['id']}/harvest")
        assert r.status_code == 422

    def test_planned_cannot_fail_directly(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        r = sacco_client.patch(f"{BASE}/{s['id']}/fail")
        assert r.status_code == 422

    def test_harvested_is_terminal_cannot_fail(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        sacco_client.patch(f"{BASE}/{s['id']}/activate")
        sacco_client.patch(f"{BASE}/{s['id']}/harvest")
        r = sacco_client.patch(f"{BASE}/{s['id']}/fail")
        assert r.status_code == 422

    def test_harvested_is_terminal_cannot_activate(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        sacco_client.patch(f"{BASE}/{s['id']}/activate")
        sacco_client.patch(f"{BASE}/{s['id']}/harvest")
        r = sacco_client.patch(f"{BASE}/{s['id']}/activate")
        assert r.status_code == 422

    def test_failed_is_terminal_cannot_activate(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        sacco_client.patch(f"{BASE}/{s['id']}/activate")
        sacco_client.patch(f"{BASE}/{s['id']}/fail")
        r = sacco_client.patch(f"{BASE}/{s['id']}/activate")
        assert r.status_code == 422

    def test_failed_is_terminal_cannot_harvest(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        sacco_client.patch(f"{BASE}/{s['id']}/activate")
        sacco_client.patch(f"{BASE}/{s['id']}/fail")
        r = sacco_client.patch(f"{BASE}/{s['id']}/harvest")
        assert r.status_code == 422

    def test_activate_nonexistent_returns_404(self, sacco_client):
        r = sacco_client.patch(f"{BASE}/{uuid.uuid4()}/activate")
        assert r.status_code == 404

    def test_harvest_nonexistent_returns_404(self, sacco_client):
        r = sacco_client.patch(f"{BASE}/{uuid.uuid4()}/harvest")
        assert r.status_code == 404

    def test_fail_nonexistent_returns_404(self, sacco_client):
        r = sacco_client.patch(f"{BASE}/{uuid.uuid4()}/fail")
        assert r.status_code == 404

    def test_transition_returns_full_season_shape(self, sacco_client, sacco_id):
        s = create_season(sacco_client, sacco_id)
        r = sacco_client.patch(f"{BASE}/{s['id']}/activate")
        body = r.json()
        assert "id" in body
        assert "farm_id" in body
        assert "crop_type" in body
        assert "status" in body
        assert "planting_date" in body
        assert "expected_harvest_date" in body
        assert "created_at" in body
