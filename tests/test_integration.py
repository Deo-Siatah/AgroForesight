"""
tests/test_integration.py
End-to-end happy-path integration test.
Walks the full SACCO → Farmer → Farm → Season → Loan → Approve → Disburse → Activate → Repay chain.
"""
from tests.conftest import rnd_phone, rnd_nid
from tests.conftest import rnd_phone, rnd_nid, sacco_admin_auth_headers

FARMERS = "/api/v1/farmers"
FARMS   = "/api/v1/farms"
SEASONS = "/api/v1/seasons"
LOANS   = "/api/v1/loans"


class TestFullHappyPath:
    """
    Complete production flow that exercises every layer:
    Repository → Service → API in sequence.
    """

    def test_repaid_journey(self, client, sacco_id):
        # 1. Register farmer
        farmer = client.post(FARMERS, json={
            "sacco_id": str(sacco_id),
            "first_name": "Joseph",
            "last_name": "Waweru",
            "phone": rnd_phone(),
            "national_id": rnd_nid(),
            "login_email": f"farmer-{uuid.uuid4().hex}@agroforesight.local",
            "login_password": "farmer123",
        }, headers=sacco_admin_auth_headers())
        assert farmer.status_code == 201
        farmer_id = farmer.json()["id"]

        # 2. Confirm profile
        profile = client.get(f"{FARMERS}/{farmer_id}")
        assert profile.status_code == 200
        assert profile.json()["farmer"]["first_name"] == "Joseph"

        # 3. Create farm
        farm = client.post(FARMS, json={
            "farmer_id": farmer_id,
            "name": "Waweru Maize Farm",
            "county": "Nakuru",
            "acreage": "5.00",
            "latitude": -0.28,
            "longitude": 36.07,
        })
        assert farm.status_code == 201
        farm_id = farm.json()["id"]

        # 4. Create season
        season = client.post(SEASONS, json={
            "farm_id": farm_id,
            "crop_type": "Maize",
            "planting_date": "2025-03-15",
            "expected_harvest_date": "2025-07-15",
        })
        assert season.status_code == 201
        season_id = season.json()["id"]
        assert season.json()["status"] == "planned"

        # 5. Activate season
        r = client.patch(f"{SEASONS}/{season_id}/activate")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

        # 6. Risk before loan — no loan yet, just to prove the endpoint works
        # (we create the loan next)

        # 7. Create loan
        loan = client.post(LOANS, json={
            "farmer_id": farmer_id,
            "amount": "120000.00",
        })
        assert loan.status_code == 201
        loan_id = loan.json()["id"]
        assert loan.json()["status"] == "pending"

        # 8. Risk — active season, score should be 0 (low)
        risk = client.get(f"{LOANS}/{loan_id}/risk?season_id={season_id}")
        assert risk.status_code == 200
        assert risk.json()["score"] == 0
        assert risk.json()["category"] == "low"

        # 9. Approve → disburse → activate loan
        assert client.patch(f"{LOANS}/{loan_id}/approve").json()["status"] == "approved"
        assert client.patch(f"{LOANS}/{loan_id}/disburse").json()["status"] == "disbursed"
        assert client.patch(f"{LOANS}/{loan_id}/activate").json()["status"] == "active"

        # 10. Harvest season
        r = client.patch(f"{SEASONS}/{season_id}/harvest")
        assert r.status_code == 200
        assert r.json()["status"] == "harvested"

        # 11. Repay loan
        r = client.patch(f"{LOANS}/{loan_id}/repay")
        assert r.status_code == 200
        assert r.json()["status"] == "repaid"

        # 12. Farmer profile now shows the loan
        profile = client.get(f"{FARMERS}/{farmer_id}")
        loans_in_profile = profile.json()["loans"]
        loan_ids = [l["id"] for l in loans_in_profile]
        assert loan_id in loan_ids

    def test_default_journey(self, client, sacco_id):
        """Alternative path: season fails → risk goes up → loan defaults."""
        farmer_id = client.post(FARMERS, json={
            "sacco_id": str(sacco_id), "first_name": "Ada", "last_name": "Otieno",
            "phone": rnd_phone(), "national_id": rnd_nid(),
            "login_email": f"farmer-{uuid.uuid4().hex}@agroforesight.local",
            "login_password": "farmer123",
        }, headers=sacco_admin_auth_headers()).json()["id"]

        farm_id = client.post(FARMS, json={
            "farmer_id": farmer_id, "name": "Otieno Farm", "county": "Kisumu",
            "acreage": "2.0", "latitude": -0.09, "longitude": 34.75,
        }).json()["id"]

        season_id = client.post(SEASONS, json={
            "farm_id": farm_id, "crop_type": "Sorghum",
            "planting_date": "2025-04-01", "expected_harvest_date": "2025-08-01",
        }).json()["id"]

        loan_id = client.post(LOANS, json={
            "farmer_id": farmer_id, "amount": "60000.00",
        }).json()["id"]

        # Activate then fail the season
        client.patch(f"{SEASONS}/{season_id}/activate")
        client.patch(f"{SEASONS}/{season_id}/fail")

        # Risk spikes to 40 (medium)
        risk = client.get(f"{LOANS}/{loan_id}/risk?season_id={season_id}")
        assert risk.json()["score"] == 40
        assert risk.json()["category"] == "medium"

        # Approve and default the loan
        client.patch(f"{LOANS}/{loan_id}/approve")
        client.patch(f"{LOANS}/{loan_id}/disburse")
        client.patch(f"{LOANS}/{loan_id}/activate")
        r = client.patch(f"{LOANS}/{loan_id}/default")
        assert r.status_code == 200
        assert r.json()["status"] == "defaulted"
