"""
tests/test_risk.py

GET  /api/v1/loans/{id}/risk
POST /api/v1/loans/{id}/risk/recalculate
"""
from __future__ import annotations

import uuid

import httpx

from tests.conftest import rnd_email, rnd_nid, rnd_phone

FARMERS = "/api/v1/farmers"
FARMS = "/api/v1/farms"
SEASONS = "/api/v1/seasons"
LOANS = "/api/v1/loans"


def _setup(client: httpx.Client, sacco_id: uuid.UUID) -> tuple[str, str]:
    """Create farmer → farm → season (PLANNED) + loan. Returns (loan_id, season_id)."""
    farmer_id = client.post(FARMERS, json={
        "sacco_id": str(sacco_id), "first_name": "R", "last_name": "S",
        "phone": rnd_phone(), "national_id": rnd_nid(),
        "login_email": rnd_email(), "login_password": "Pass!1",
    }).json()["id"]

    farm_id = client.post(FARMS, json={
        "farmer_id": farmer_id, "name": "Risk Farm",
        "county": "Nakuru", "acreage": "3.0",
        "latitude": -0.30, "longitude": 36.10,
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


# ---------------------------------------------------------------------------
# GET /api/v1/loans/{id}/risk
# ---------------------------------------------------------------------------

class TestRiskScore:
    def test_no_season_score_0_category_low(self, sacco_client, sacco_id):
        loan_id, _ = _setup(sacco_client, sacco_id)
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk")
        assert r.status_code == 200
        body = r.json()
        assert body["score"] == 0
        assert body["category"] == "low"
        assert body["loan_id"] == loan_id

    def test_planned_season_score_0(self, sacco_client, sacco_id):
        loan_id, season_id = _setup(sacco_client, sacco_id)
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert r.status_code == 200
        assert r.json()["score"] == 0

    def test_active_season_score_0(self, sacco_client, sacco_id):
        loan_id, season_id = _setup(sacco_client, sacco_id)
        sacco_client.patch(f"{SEASONS}/{season_id}/activate")
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert r.status_code == 200
        assert r.json()["score"] == 0

    def test_failed_season_score_40_medium(self, sacco_client, sacco_id):
        loan_id, season_id = _setup(sacco_client, sacco_id)
        sacco_client.patch(f"{SEASONS}/{season_id}/activate")
        sacco_client.patch(f"{SEASONS}/{season_id}/fail")
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert r.status_code == 200
        body = r.json()
        assert body["score"] == 40
        assert body["category"] == "medium"
        assert body["loan_id"] == loan_id

    def test_harvested_season_score_0_low(self, sacco_client, sacco_id):
        loan_id, season_id = _setup(sacco_client, sacco_id)
        sacco_client.patch(f"{SEASONS}/{season_id}/activate")
        sacco_client.patch(f"{SEASONS}/{season_id}/harvest")
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert r.status_code == 200
        body = r.json()
        assert body["score"] == 0
        assert body["category"] == "low"

    def test_score_capped_at_100(self, sacco_client, sacco_id):
        """Verify score never exceeds 100 even in worst-case scenario."""
        loan_id, season_id = _setup(sacco_client, sacco_id)
        sacco_client.patch(f"{SEASONS}/{season_id}/activate")
        sacco_client.patch(f"{SEASONS}/{season_id}/fail")
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert r.json()["score"] <= 100

    def test_response_shape(self, sacco_client, sacco_id):
        loan_id, _ = _setup(sacco_client, sacco_id)
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk")
        body = r.json()
        assert "loan_id" in body
        assert "score" in body
        assert "category" in body

    def test_category_values_are_valid(self, sacco_client, sacco_id):
        loan_id, season_id = _setup(sacco_client, sacco_id)
        for state_steps in [[], ["activate"], ["activate", "fail"], ["activate", "harvest"]]:
            _, sid = _setup(sacco_client, sacco_id)
            for step in state_steps:
                sacco_client.patch(f"{SEASONS}/{sid}/{step}")
            r = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": sid})
            assert r.json()["category"] in ("low", "medium", "high")

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        loan_id, _ = _setup(sacco_client, sacco_id)
        r = httpx.get(f"http://127.0.0.1:8000{LOANS}/{loan_id}/risk", timeout=10)
        assert r.status_code == 401

    def test_unknown_loan_returns_404(self, sacco_client):
        r = sacco_client.get(f"{LOANS}/{uuid.uuid4()}/risk")
        assert r.status_code == 404

    def test_unknown_season_id_returns_404(self, sacco_client, sacco_id):
        loan_id, _ = _setup(sacco_client, sacco_id)
        r = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": str(uuid.uuid4())})
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/v1/loans/{id}/risk/recalculate
# ---------------------------------------------------------------------------

class TestRecalculateRisk:
    def test_recalculate_returns_same_shape(self, sacco_client, sacco_id):
        loan_id, season_id = _setup(sacco_client, sacco_id)
        sacco_client.patch(f"{SEASONS}/{season_id}/activate")
        sacco_client.patch(f"{SEASONS}/{season_id}/fail")
        r = sacco_client.post(f"{LOANS}/{loan_id}/risk/recalculate",
                              params={"season_id": season_id})
        assert r.status_code == 200
        body = r.json()
        assert body["score"] == 40
        assert body["category"] == "medium"
        assert body["loan_id"] == loan_id

    def test_recalculate_no_season_score_0(self, sacco_client, sacco_id):
        loan_id, _ = _setup(sacco_client, sacco_id)
        r = sacco_client.post(f"{LOANS}/{loan_id}/risk/recalculate")
        assert r.status_code == 200
        assert r.json()["score"] == 0

    def test_recalculate_unknown_loan_returns_404(self, sacco_client):
        r = sacco_client.post(f"{LOANS}/{uuid.uuid4()}/risk/recalculate")
        assert r.status_code == 404

    def test_recalculate_unauthenticated_returns_401(self, sacco_client, sacco_id):
        loan_id, _ = _setup(sacco_client, sacco_id)
        r = httpx.post(f"http://127.0.0.1:8000{LOANS}/{loan_id}/risk/recalculate", timeout=10)
        assert r.status_code == 401
