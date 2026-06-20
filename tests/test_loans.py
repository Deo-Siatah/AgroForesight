"""
tests/test_loans.py
Integration tests for Loan CRUD and full status transition chain.
"""
import uuid
from tests.conftest import rnd_phone, rnd_nid
from tests.conftest import rnd_phone, rnd_nid, sacco_admin_auth_headers

FARMERS = "/api/v1/farmers"
BASE    = "/api/v1/loans"


def _farmer_id(client, sacco_id):
    return client.post(FARMERS, json={
        "sacco_id": str(sacco_id), "first_name": "L", "last_name": "T",
        "phone": rnd_phone(), "national_id": rnd_nid(),
        "login_email": f"farmer-{uuid.uuid4().hex}@agroforesight.local",
        "login_password": "farmer123",
    }, headers=sacco_admin_auth_headers()).json()["id"]


def _new_loan(client, sacco_id, amount="50000.00"):
    fid = _farmer_id(client, sacco_id)
    return client.post(BASE, json={"farmer_id": fid, "amount": amount}).json()


class TestCreateLoan:
    def test_success_returns_201_pending(self, client, sacco_id):
        fid = _farmer_id(client, sacco_id)
        r = client.post(BASE, json={"farmer_id": fid, "amount": "75000.00"})
        assert r.status_code == 201
        body = r.json()
        assert body["status"] == "pending"
        assert body["risk_score"] is None

    def test_farmer_not_found_returns_404(self, client):
        r = client.post(BASE, json={"farmer_id": str(uuid.uuid4()), "amount": "1000"})
        assert r.status_code == 404

    def test_negative_amount_returns_422(self, client, sacco_id):
        fid = _farmer_id(client, sacco_id)
        r = client.post(BASE, json={"farmer_id": fid, "amount": "-500"})
        assert r.status_code == 422

    def test_zero_amount_returns_422(self, client, sacco_id):
        fid = _farmer_id(client, sacco_id)
        r = client.post(BASE, json={"farmer_id": fid, "amount": "0"})
        assert r.status_code == 422


class TestGetLoan:
    def test_success(self, client, sacco_id):
        loan = _new_loan(client, sacco_id)
        r = client.get(f"{BASE}/{loan['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == loan["id"]

    def test_not_found_returns_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404


class TestLoanApprovalChain:
    def test_full_repaid_chain(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        assert client.patch(f"{BASE}/{lid}/approve").json()["status"] == "approved"
        assert client.patch(f"{BASE}/{lid}/disburse").json()["status"] == "disbursed"
        assert client.patch(f"{BASE}/{lid}/activate").json()["status"] == "active"
        assert client.patch(f"{BASE}/{lid}/repay").json()["status"] == "repaid"

    def test_full_defaulted_chain(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        client.patch(f"{BASE}/{lid}/approve")
        client.patch(f"{BASE}/{lid}/disburse")
        client.patch(f"{BASE}/{lid}/activate")
        assert client.patch(f"{BASE}/{lid}/default").json()["status"] == "defaulted"

    def test_reject_from_pending(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        assert client.patch(f"{BASE}/{lid}/reject").json()["status"] == "rejected"

    def test_reject_from_approved(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        client.patch(f"{BASE}/{lid}/approve")
        assert client.patch(f"{BASE}/{lid}/reject").json()["status"] == "rejected"


class TestInvalidLoanTransitions:
    def test_pending_cannot_disburse_directly(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        assert client.patch(f"{BASE}/{lid}/disburse").status_code == 422

    def test_repaid_is_terminal(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        client.patch(f"{BASE}/{lid}/approve")
        client.patch(f"{BASE}/{lid}/disburse")
        client.patch(f"{BASE}/{lid}/activate")
        client.patch(f"{BASE}/{lid}/repay")
        assert client.patch(f"{BASE}/{lid}/approve").status_code == 422

    def test_defaulted_is_terminal(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        client.patch(f"{BASE}/{lid}/approve")
        client.patch(f"{BASE}/{lid}/disburse")
        client.patch(f"{BASE}/{lid}/activate")
        client.patch(f"{BASE}/{lid}/default")
        assert client.patch(f"{BASE}/{lid}/approve").status_code == 422

    def test_rejected_is_terminal(self, client, sacco_id):
        lid = _new_loan(client, sacco_id)["id"]
        client.patch(f"{BASE}/{lid}/reject")
        assert client.patch(f"{BASE}/{lid}/approve").status_code == 422

    def test_nonexistent_returns_404(self, client):
        assert client.patch(f"{BASE}/{uuid.uuid4()}/approve").status_code == 404
