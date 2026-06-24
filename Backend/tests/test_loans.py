"""
tests/test_loans.py

POST   /api/v1/loans
GET    /api/v1/loans/{id}
PATCH  /api/v1/loans/{id}/approve
PATCH  /api/v1/loans/{id}/reject
PATCH  /api/v1/loans/{id}/disburse
PATCH  /api/v1/loans/{id}/activate
PATCH  /api/v1/loans/{id}/repay
PATCH  /api/v1/loans/{id}/default
"""
from __future__ import annotations

import uuid

import httpx

from tests.conftest import rnd_email, rnd_nid, rnd_phone

FARMERS = "/api/v1/farmers"
BASE = "/api/v1/loans"


def _make_farmer(client: httpx.Client, sacco_id: uuid.UUID) -> str:
    r = client.post(FARMERS, json={
        "sacco_id": str(sacco_id), "first_name": "L", "last_name": "T",
        "phone": rnd_phone(), "national_id": rnd_nid(),
        "login_email": rnd_email(), "login_password": "Pass!1",
    })
    assert r.status_code == 201, r.text
    return r.json()["id"]


def create_loan(client: httpx.Client, sacco_id: uuid.UUID, amount: str = "50000.00") -> dict:
    fid = _make_farmer(client, sacco_id)
    r = client.post(BASE, json={"farmer_id": fid, "amount": amount})
    assert r.status_code == 201, r.text
    return r.json()


def _advance_to(client: httpx.Client, loan_id: str, *steps: str) -> None:
    """Walk a loan through the given sequence of transition endpoints."""
    for step in steps:
        r = client.patch(f"{BASE}/{loan_id}/{step}")
        assert r.status_code == 200, f"Step '{step}' failed: {r.text}"


# ---------------------------------------------------------------------------
# POST /api/v1/loans
# ---------------------------------------------------------------------------

class TestCreateLoan:
    def test_sacco_admin_creates_loan_201_pending(self, sacco_client, sacco_id):
        fid = _make_farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json={"farmer_id": fid, "amount": "75000.00"})
        assert r.status_code == 201
        body = r.json()
        assert body["status"] == "pending"
        assert body["risk_score"] is None
        assert body["farmer_id"] == fid
        assert "id" in body
        assert "created_at" in body

    def test_admin_creates_loan_201(self, admin_client, sacco_client, sacco_id):
        fid = _make_farmer(sacco_client, sacco_id)
        r = admin_client.post(BASE, json={"farmer_id": fid, "amount": "10000.00"})
        assert r.status_code == 201

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        fid = _make_farmer(sacco_client, sacco_id)
        r = httpx.post("http://127.0.0.1:8000" + BASE,
                       json={"farmer_id": fid, "amount": "1000"}, timeout=10)
        assert r.status_code == 401

    def test_farmer_role_cannot_create_loan_403(self, sacco_client, sacco_id):
        from tests.conftest import login, auth
        email = rnd_email()
        farmer = sacco_client.post(FARMERS, json={
            "sacco_id": str(sacco_id), "first_name": "F", "last_name": "U",
            "phone": rnd_phone(), "national_id": rnd_nid(),
            "login_email": email, "login_password": "Pass!1",
        }).json()
        token = login(email, "Pass!1")
        r = httpx.post(
            "http://127.0.0.1:8000" + BASE,
            json={"farmer_id": farmer["id"], "amount": "1000"},
            headers=auth(token), timeout=10,
        )
        assert r.status_code == 403

    def test_farmer_not_found_returns_404(self, sacco_client):
        r = sacco_client.post(BASE, json={"farmer_id": str(uuid.uuid4()), "amount": "1000"})
        assert r.status_code == 404

    def test_zero_amount_returns_422(self, sacco_client, sacco_id):
        fid = _make_farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json={"farmer_id": fid, "amount": "0"})
        assert r.status_code == 422

    def test_negative_amount_returns_422(self, sacco_client, sacco_id):
        fid = _make_farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json={"farmer_id": fid, "amount": "-500"})
        assert r.status_code == 422

    def test_missing_amount_returns_422(self, sacco_client, sacco_id):
        fid = _make_farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json={"farmer_id": fid})
        assert r.status_code == 422

    def test_string_amount_returns_422(self, sacco_client, sacco_id):
        fid = _make_farmer(sacco_client, sacco_id)
        r = sacco_client.post(BASE, json={"farmer_id": fid, "amount": "much money"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/loans/{id}
# ---------------------------------------------------------------------------

class TestGetLoan:
    def test_sacco_admin_fetches_loan(self, sacco_client, sacco_id):
        loan = create_loan(sacco_client, sacco_id)
        r = sacco_client.get(f"{BASE}/{loan['id']}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == loan["id"]
        assert "status" in body
        assert "amount" in body

    def test_unauthenticated_returns_401(self, sacco_client, sacco_id):
        loan = create_loan(sacco_client, sacco_id)
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/{loan['id']}", timeout=10)
        assert r.status_code == 401

    def test_unknown_id_returns_404(self, sacco_client):
        r = sacco_client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404

    def test_invalid_uuid_returns_422(self, sacco_client):
        r = sacco_client.get(f"{BASE}/not-a-uuid")
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Valid transition chains
# ---------------------------------------------------------------------------

class TestValidTransitions:
    def test_full_repaid_chain(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        assert sacco_client.patch(f"{BASE}/{lid}/approve").json()["status"] == "approved"
        assert sacco_client.patch(f"{BASE}/{lid}/disburse").json()["status"] == "disbursed"
        assert sacco_client.patch(f"{BASE}/{lid}/activate").json()["status"] == "active"
        assert sacco_client.patch(f"{BASE}/{lid}/repay").json()["status"] == "repaid"

    def test_full_defaulted_chain(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        _advance_to(sacco_client, lid, "approve", "disburse", "activate")
        assert sacco_client.patch(f"{BASE}/{lid}/default").json()["status"] == "defaulted"

    def test_reject_from_pending(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        r = sacco_client.patch(f"{BASE}/{lid}/reject")
        assert r.status_code == 200
        assert r.json()["status"] == "rejected"

    def test_reject_from_approved(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        sacco_client.patch(f"{BASE}/{lid}/approve")
        r = sacco_client.patch(f"{BASE}/{lid}/reject")
        assert r.status_code == 200
        assert r.json()["status"] == "rejected"

    def test_transition_response_has_full_loan_shape(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        r = sacco_client.patch(f"{BASE}/{lid}/approve")
        body = r.json()
        assert "id" in body
        assert "farmer_id" in body
        assert "amount" in body
        assert "status" in body
        assert "risk_score" in body
        assert "created_at" in body


# ---------------------------------------------------------------------------
# Invalid transitions (422)
# ---------------------------------------------------------------------------

class TestInvalidTransitions:
    def test_pending_cannot_disburse_directly(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        assert sacco_client.patch(f"{BASE}/{lid}/disburse").status_code == 422

    def test_pending_cannot_activate_directly(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        assert sacco_client.patch(f"{BASE}/{lid}/activate").status_code == 422

    def test_pending_cannot_repay_directly(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        assert sacco_client.patch(f"{BASE}/{lid}/repay").status_code == 422

    def test_pending_cannot_default_directly(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        assert sacco_client.patch(f"{BASE}/{lid}/default").status_code == 422

    def test_approved_cannot_activate_directly(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        sacco_client.patch(f"{BASE}/{lid}/approve")
        assert sacco_client.patch(f"{BASE}/{lid}/activate").status_code == 422

    def test_approved_cannot_repay_directly(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        sacco_client.patch(f"{BASE}/{lid}/approve")
        assert sacco_client.patch(f"{BASE}/{lid}/repay").status_code == 422

    def test_repaid_is_terminal(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        _advance_to(sacco_client, lid, "approve", "disburse", "activate", "repay")
        for step in ("approve", "reject", "disburse", "activate", "default"):
            assert sacco_client.patch(f"{BASE}/{lid}/{step}").status_code == 422, step

    def test_defaulted_is_terminal(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        _advance_to(sacco_client, lid, "approve", "disburse", "activate", "default")
        for step in ("approve", "reject", "disburse", "activate", "repay"):
            assert sacco_client.patch(f"{BASE}/{lid}/{step}").status_code == 422, step

    def test_rejected_is_terminal(self, sacco_client, sacco_id):
        lid = create_loan(sacco_client, sacco_id)["id"]
        sacco_client.patch(f"{BASE}/{lid}/reject")
        for step in ("approve", "disburse", "activate", "repay", "default"):
            assert sacco_client.patch(f"{BASE}/{lid}/{step}").status_code == 422, step

    def test_nonexistent_loan_approve_returns_404(self, sacco_client):
        assert sacco_client.patch(f"{BASE}/{uuid.uuid4()}/approve").status_code == 404

    def test_nonexistent_loan_reject_returns_404(self, sacco_client):
        assert sacco_client.patch(f"{BASE}/{uuid.uuid4()}/reject").status_code == 404
