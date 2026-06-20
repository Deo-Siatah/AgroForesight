"""
tests/test_risk.py
Integration tests for GET /api/v1/loans/{id}/risk and POST .../risk/recalculate.
"""
import uuid
from tests.conftest import rnd_phone, rnd_nid
from tests.conftest import rnd_phone, rnd_nid, sacco_admin_auth_headers

FARMERS = "/api/v1/farmers"
FARMS   = "/api/v1/farms"
SEASONS = "/api/v1/seasons"
LOANS   = "/api/v1/loans"


def _setup(client, sacco_id):
    """Returns (loan_id, season_id). Season is left in PLANNED status."""
    farmer_id = client.post(FARMERS, json={
        "sacco_id": str(sacco_id), "first_name": "R", "last_name": "S",
        "phone": rnd_phone(), "national_id": rnd_nid(),
        "login_email": f"farmer-{uuid.uuid4().hex}@agroforesight.local",
        "login_password": "farmer123",
    }, headers=sacco_admin_auth_headers()).json()["id"]

    farm_id = client.post(FARMS, json={
        "farmer_id": farmer_id, "name": "Risk Farm",
        "county": "Nakuru", "acreage": "3.0",
        "latitude": -0.3, "longitude": 36.1,
    }).json()["id"]

    season_id = client.post(SEASONS, json={
        "farm_id": farm_id, "crop_type": "Maize",
        "planting_date": "2025-03-01",
        "expected_harvest_date": "2025-07-01",
    }).json()["id"]

    loan_id = client.post(LOANS, json={
        "farmer_id": farmer_id, "amount": "80000.00",
    }).json()["id"]

    return loan_id, season_id


class TestRiskScore:
    def test_no_season_score_is_zero_low(self, client, sacco_id):
        loan_id, _ = _setup(client, sacco_id)
        r = client.get(f"{LOANS}/{loan_id}/risk")
        assert r.status_code == 200
        body = r.json()
        assert body["score"] == 0
        assert body["category"] == "low"

    def test_planned_season_score_is_zero(self, client, sacco_id):
        loan_id, season_id = _setup(client, sacco_id)
        r = client.get(f"{LOANS}/{loan_id}/risk?season_id={season_id}")
        assert r.status_code == 200
        assert r.json()["score"] == 0

    def test_active_season_score_is_zero(self, client, sacco_id):
        loan_id, season_id = _setup(client, sacco_id)
        client.patch(f"{SEASONS}/{season_id}/activate")
        r = client.get(f"{LOANS}/{loan_id}/risk?season_id={season_id}")
        assert r.status_code == 200
        assert r.json()["score"] == 0

    def test_failed_season_score_is_40_medium(self, client, sacco_id):
        loan_id, season_id = _setup(client, sacco_id)
        client.patch(f"{SEASONS}/{season_id}/activate")
        client.patch(f"{SEASONS}/{season_id}/fail")
        r = client.get(f"{LOANS}/{loan_id}/risk?season_id={season_id}")
        assert r.status_code == 200
        body = r.json()
        assert body["score"] == 40
        assert body["category"] == "medium"
        assert body["loan_id"] == loan_id

    def test_harvested_season_score_is_zero(self, client, sacco_id):
        loan_id, season_id = _setup(client, sacco_id)
        client.patch(f"{SEASONS}/{season_id}/activate")
        client.patch(f"{SEASONS}/{season_id}/harvest")
        r = client.get(f"{LOANS}/{loan_id}/risk?season_id={season_id}")
        assert r.status_code == 200
        assert r.json()["score"] == 0

    def test_loan_not_found_returns_404(self, client):
        r = client.get(f"{LOANS}/{uuid.uuid4()}/risk")
        assert r.status_code == 404

    def test_recalculate_endpoint_returns_same_shape(self, client, sacco_id):
        loan_id, season_id = _setup(client, sacco_id)
        client.patch(f"{SEASONS}/{season_id}/activate")
        client.patch(f"{SEASONS}/{season_id}/fail")
        r = client.post(f"{LOANS}/{loan_id}/risk/recalculate?season_id={season_id}")
        assert r.status_code == 200
        body = r.json()
        assert "score" in body
        assert "category" in body
        assert "loan_id" in body
