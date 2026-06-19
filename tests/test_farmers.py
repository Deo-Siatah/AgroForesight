"""
tests/test_farmers.py
Integration tests for POST /api/v1/farmers and GET /api/v1/farmers/{id}.
"""
import uuid
from tests.conftest import rnd_phone, rnd_nid


BASE = "/api/v1/farmers"


def _payload(sacco_id, **overrides):
    return {
        "sacco_id": str(sacco_id),
        "first_name": "Jane",
        "last_name": "Wanjiku",
        "phone": rnd_phone(),
        "national_id": rnd_nid(),
        **overrides,
    }


# ---------------------------------------------------------------------------
# POST /api/v1/farmers
# ---------------------------------------------------------------------------

class TestRegisterFarmer:
    def test_success_returns_201(self, client, sacco_id):
        r = client.post(BASE, json=_payload(sacco_id))
        assert r.status_code == 201
        body = r.json()
        assert body["first_name"] == "Jane"
        assert body["sacco_id"] == str(sacco_id)
        assert "id" in body
        assert "created_at" in body

    def test_duplicate_phone_returns_409(self, client, sacco_id):
        phone = rnd_phone()
        client.post(BASE, json=_payload(sacco_id, phone=phone))
        r = client.post(BASE, json=_payload(sacco_id, phone=phone))
        assert r.status_code == 409
        assert "phone" in r.json()["detail"].lower()

    def test_duplicate_national_id_returns_409(self, client, sacco_id):
        nid = rnd_nid()
        client.post(BASE, json=_payload(sacco_id, national_id=nid))
        r = client.post(BASE, json=_payload(sacco_id, national_id=nid))
        assert r.status_code == 409
        assert "national" in r.json()["detail"].lower()

    def test_invalid_phone_returns_422(self, client, sacco_id):
        r = client.post(BASE, json=_payload(sacco_id, phone="not-a-phone"))
        assert r.status_code == 422

    def test_empty_first_name_returns_422(self, client, sacco_id):
        r = client.post(BASE, json=_payload(sacco_id, first_name=""))
        assert r.status_code == 422

    def test_missing_sacco_id_returns_422(self, client):
        r = client.post(BASE, json={"first_name": "X", "last_name": "Y", "phone": rnd_phone()})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/farmers/{id}
# ---------------------------------------------------------------------------

class TestGetFarmerProfile:
    def test_returns_farmer_with_farms_and_loans(self, client, sacco_id):
        created = client.post(BASE, json=_payload(sacco_id)).json()
        r = client.get(f"{BASE}/{created['id']}")
        assert r.status_code == 200
        body = r.json()
        assert body["farmer"]["id"] == created["id"]
        assert isinstance(body["farms"], list)
        assert isinstance(body["loans"], list)

    def test_unknown_id_returns_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404
