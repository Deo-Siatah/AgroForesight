"""
tests/test_integration.py

End-to-end journeys that walk the full system flow:
  Admin creates SACCO → SACCO admin registers farmer → creates farm
  → opens season → opens loan → processes loan → closes season → closes loan.

Two paths: happy (repaid) and risk (failed season → defaulted loan).
"""
from __future__ import annotations

from tests.conftest import rnd_email, rnd_nid, rnd_phone

FARMERS = "/api/v1/farmers"
FARMS = "/api/v1/farms"
SEASONS = "/api/v1/seasons"
LOANS = "/api/v1/loans"


class TestRepaidJourney:
    """
    Full sunny-day path:
    SACCO → Farmer → Farm → Season(planned→active) → Loan(pending→approved→disbursed→active)
    → Season(harvested) → Loan(repaid)
    Risk stays at 0 throughout.
    """

    def test_full_repaid_journey(self, admin_client, sacco_client, sacco_id):
        # 1. Confirm the SACCO is readable by admin
        r = admin_client.get(f"/api/v1/saccos/{sacco_id}")
        assert r.status_code == 200
        assert r.json()["id"] == str(sacco_id)

        # 2. Register farmer
        farmer = sacco_client.post(FARMERS, json={
            "sacco_id": str(sacco_id),
            "first_name": "Joseph",
            "last_name": "Waweru",
            "phone": rnd_phone(),
            "national_id": rnd_nid(),
            "login_email": rnd_email(),
            "login_password": "Farmer!Pass1",
        })
        assert farmer.status_code == 201
        farmer_id = farmer.json()["id"]
        assert farmer.json()["sacco_id"] == str(sacco_id)

        # 3. Confirm farmer profile shape
        profile = sacco_client.get(f"{FARMERS}/{farmer_id}")
        assert profile.status_code == 200
        assert profile.json()["farmer"]["first_name"] == "Joseph"
        assert profile.json()["farms"] == []
        assert profile.json()["loans"] == []

        # 4. Create farm
        farm = sacco_client.post(FARMS, json={
            "farmer_id": farmer_id,
            "name": "Waweru Maize Farm",
            "county": "Nakuru",
            "acreage": "5.00",
            "latitude": -0.28,
            "longitude": 36.07,
        })
        assert farm.status_code == 201
        farm_id = farm.json()["id"]

        # 5. Create season — starts PLANNED
        season = sacco_client.post(SEASONS, json={
            "farm_id": farm_id,
            "crop_type": "Maize",
            "planting_date": "2025-03-15",
            "expected_harvest_date": "2025-07-15",
        })
        assert season.status_code == 201
        season_id = season.json()["id"]
        assert season.json()["status"] == "planned"

        # 6. Activate season
        r = sacco_client.patch(f"{SEASONS}/{season_id}/activate")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

        # 7. Create loan — starts PENDING
        loan = sacco_client.post(LOANS, json={
            "farmer_id": farmer_id,
            "amount": "120000.00",
        })
        assert loan.status_code == 201
        loan_id = loan.json()["id"]
        assert loan.json()["status"] == "pending"

        # 8. Risk on active season — score 0, category low
        risk = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert risk.status_code == 200
        assert risk.json()["score"] == 0
        assert risk.json()["category"] == "low"

        # 9. Drive loan through full approval chain
        r = sacco_client.patch(f"{LOANS}/{loan_id}/approve")
        assert r.status_code == 200
        assert r.json()["status"] == "approved"

        r = sacco_client.patch(f"{LOANS}/{loan_id}/disburse")
        assert r.status_code == 200
        assert r.json()["status"] == "disbursed"

        r = sacco_client.patch(f"{LOANS}/{loan_id}/activate")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

        # 10. Harvest season
        r = sacco_client.patch(f"{SEASONS}/{season_id}/harvest")
        assert r.status_code == 200
        assert r.json()["status"] == "harvested"

        # 11. Risk after harvest — still 0
        risk = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert risk.json()["score"] == 0

        # 12. Repay loan
        r = sacco_client.patch(f"{LOANS}/{loan_id}/repay")
        assert r.status_code == 200
        assert r.json()["status"] == "repaid"

        # 13. Farmer profile now lists the loan and farm
        profile = sacco_client.get(f"{FARMERS}/{farmer_id}")
        assert profile.status_code == 200
        body = profile.json()
        loan_ids = [l["id"] for l in body["loans"]]
        farm_ids = [f["id"] for f in body["farms"]]
        assert loan_id in loan_ids
        assert farm_id in farm_ids

        # 14. Repaid is terminal — any further transition must fail
        assert sacco_client.patch(f"{LOANS}/{loan_id}/approve").status_code == 422


class TestDefaultedJourney:
    """
    Risk path: season fails mid-season → risk spikes to 40 (medium)
    → SACCO decides to approve anyway → loan eventually defaults.
    """

    def test_full_defaulted_journey(self, sacco_client, sacco_id):
        # 1. Register farmer
        farmer_id = sacco_client.post(FARMERS, json={
            "sacco_id": str(sacco_id),
            "first_name": "Ada",
            "last_name": "Otieno",
            "phone": rnd_phone(),
            "national_id": rnd_nid(),
            "login_email": rnd_email(),
            "login_password": "Farmer!Pass1",
        }).json()["id"]

        # 2. Create farm
        farm_id = sacco_client.post(FARMS, json={
            "farmer_id": farmer_id,
            "name": "Otieno Sorghum Farm",
            "county": "Kisumu",
            "acreage": "2.0",
            "latitude": -0.09,
            "longitude": 34.75,
        }).json()["id"]

        # 3. Create and activate season
        season_id = sacco_client.post(SEASONS, json={
            "farm_id": farm_id,
            "crop_type": "Sorghum",
            "planting_date": "2025-04-01",
            "expected_harvest_date": "2025-08-01",
        }).json()["id"]

        sacco_client.patch(f"{SEASONS}/{season_id}/activate")

        # 4. Create loan
        loan_id = sacco_client.post(LOANS, json={
            "farmer_id": farmer_id,
            "amount": "60000.00",
        }).json()["id"]

        # 5. Season fails — risk spikes
        sacco_client.patch(f"{SEASONS}/{season_id}/fail")

        risk = sacco_client.get(f"{LOANS}/{loan_id}/risk", params={"season_id": season_id})
        assert risk.status_code == 200
        assert risk.json()["score"] == 40
        assert risk.json()["category"] == "medium"

        # 6. SACCO approves anyway — drives full chain
        sacco_client.patch(f"{LOANS}/{loan_id}/approve")
        sacco_client.patch(f"{LOANS}/{loan_id}/disburse")
        sacco_client.patch(f"{LOANS}/{loan_id}/activate")

        # 7. Default
        r = sacco_client.patch(f"{LOANS}/{loan_id}/default")
        assert r.status_code == 200
        assert r.json()["status"] == "defaulted"

        # 8. Defaulted is terminal
        assert sacco_client.patch(f"{LOANS}/{loan_id}/approve").status_code == 422

        # 9. Recalculate risk on a failed season still returns 40
        risk = sacco_client.post(f"{LOANS}/{loan_id}/risk/recalculate",
                                 params={"season_id": season_id})
        assert risk.json()["score"] == 40
