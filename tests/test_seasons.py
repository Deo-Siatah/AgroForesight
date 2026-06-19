"""
tests/test_seasons.py
Integration tests for Season CRUD and status transitions.
"""
import uuid
from tests.conftest import rnd_phone, rnd_nid

FARMERS = "/api/v1/farmers"
FARMS   = "/api/v1/farms"
BASE    = "/api/v1/seasons"


def _setup(client, sacco_id):
    """Create a farmer + farm, return farm_id."""
    farmer = client.post(FARMERS, json={
        "sacco_id": str(sacco_id), "first_name": "A", "last_name": "B",
        "phone": rnd_phone(), "national_id": rnd_nid(),
    }).json()
    farm = client.post(FARMS, json={
        "farmer_id": farmer["id"], "name": "Season Farm",
        "county": "Nakuru", "acreage": "1.0",
        "latitude": -0.3, "longitude": 36.1,
    }).json()
    return farm["id"]


def _season_payload(farm_id, **overrides):
    return {
        "farm_id": str(farm_id),
        "crop_type": "Maize",
        "planting_date": "2025-03-01",
        "expected_harvest_date": "2025-07-01",
        **overrides,
    }


class TestCreateSeason:
    def test_success_returns_201_with_planned_status(self, client, sacco_id):
        farm_id = _setup(client, sacco_id)
        r = client.post(BASE, json=_season_payload(farm_id))
        assert r.status_code == 201
        assert r.json()["status"] == "planned"

    def test_farm_not_found_returns_404(self, client):
        r = client.post(BASE, json=_season_payload(uuid.uuid4()))
        assert r.status_code == 404

    def test_inverted_dates_returns_422(self, client, sacco_id):
        farm_id = _setup(client, sacco_id)
        r = client.post(BASE, json=_season_payload(
            farm_id, planting_date="2025-07-01", expected_harvest_date="2025-03-01"
        ))
        assert r.status_code == 422

    def test_same_dates_returns_422(self, client, sacco_id):
        farm_id = _setup(client, sacco_id)
        r = client.post(BASE, json=_season_payload(
            farm_id, planting_date="2025-03-01", expected_harvest_date="2025-03-01"
        ))
        assert r.status_code == 422


class TestGetSeason:
    def test_success(self, client, sacco_id):
        farm_id = _setup(client, sacco_id)
        season = client.post(BASE, json=_season_payload(farm_id)).json()
        r = client.get(f"{BASE}/{season['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == season["id"]

    def test_not_found_returns_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


class TestSeasonTransitions:
    def _new_season(self, client, sacco_id):
        farm_id = _setup(client, sacco_id)
        return client.post(BASE, json=_season_payload(farm_id)).json()

    def test_planned_to_active(self, client, sacco_id):
        s = self._new_season(client, sacco_id)
        r = client.patch(f"{BASE}/{s['id']}/activate")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

    def test_active_to_harvested(self, client, sacco_id):
        s = self._new_season(client, sacco_id)
        client.patch(f"{BASE}/{s['id']}/activate")
        r = client.patch(f"{BASE}/{s['id']}/harvest")
        assert r.status_code == 200
        assert r.json()["status"] == "harvested"

    def test_active_to_failed(self, client, sacco_id):
        s = self._new_season(client, sacco_id)
        client.patch(f"{BASE}/{s['id']}/activate")
        r = client.patch(f"{BASE}/{s['id']}/fail")
        assert r.status_code == 200
        assert r.json()["status"] == "failed"

    def test_planned_cannot_harvest_directly(self, client, sacco_id):
        s = self._new_season(client, sacco_id)
        r = client.patch(f"{BASE}/{s['id']}/harvest")
        assert r.status_code == 422

    def test_harvested_is_terminal(self, client, sacco_id):
        s = self._new_season(client, sacco_id)
        client.patch(f"{BASE}/{s['id']}/activate")
        client.patch(f"{BASE}/{s['id']}/harvest")
        r = client.patch(f"{BASE}/{s['id']}/fail")  # terminal → fail blocked
        assert r.status_code == 422

    def test_failed_is_terminal(self, client, sacco_id):
        s = self._new_season(client, sacco_id)
        client.patch(f"{BASE}/{s['id']}/activate")
        client.patch(f"{BASE}/{s['id']}/fail")
        r = client.patch(f"{BASE}/{s['id']}/activate")  # terminal → re-activate blocked
        assert r.status_code == 422

    def test_activate_nonexistent_returns_404(self, client):
        r = client.patch(f"{BASE}/{uuid.uuid4()}/activate")
        assert r.status_code == 404
