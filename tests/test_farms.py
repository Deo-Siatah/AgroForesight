"""
tests/test_farms.py
Integration tests for POST /api/v1/farms and GET /api/v1/farms/{id}.
"""
import uuid
from tests.conftest import rnd_phone, rnd_nid

FARMERS = "/api/v1/farmers"
BASE = "/api/v1/farms"


def _farmer(client, sacco_id):
    return client.post(FARMERS, json={
        "sacco_id": str(sacco_id),
        "first_name": "Test",
        "last_name": "Farmer",
        "phone": rnd_phone(),
        "national_id": rnd_nid(),
    }).json()


def _payload(farmer_id, **overrides):
    return {
        "farmer_id": str(farmer_id),
        "name": "Wanjiku Farm",
        "county": "Nakuru",
        "acreage": "2.50",
        "latitude": -0.3,
        "longitude": 36.1,
        **overrides,
    }


class TestCreateFarm:
    def test_success_returns_201(self, client, sacco_id):
        farmer = _farmer(client, sacco_id)
        r = client.post(BASE, json=_payload(farmer["id"]))
        assert r.status_code == 201
        body = r.json()
        assert body["farmer_id"] == farmer["id"]
        assert float(body["acreage"]) == 2.50

    def test_farmer_not_found_returns_404(self, client):
        r = client.post(BASE, json=_payload(uuid.uuid4()))
        assert r.status_code == 404

    def test_latitude_outside_kenya_returns_422(self, client, sacco_id):
        farmer = _farmer(client, sacco_id)
        r = client.post(BASE, json=_payload(farmer["id"], latitude=50.0))
        assert r.status_code == 422

    def test_longitude_outside_kenya_returns_422(self, client, sacco_id):
        farmer = _farmer(client, sacco_id)
        r = client.post(BASE, json=_payload(farmer["id"], longitude=10.0))
        assert r.status_code == 422

    def test_negative_acreage_returns_422(self, client, sacco_id):
        farmer = _farmer(client, sacco_id)
        r = client.post(BASE, json=_payload(farmer["id"], acreage="-1.0"))
        assert r.status_code == 422

    def test_zero_acreage_returns_422(self, client, sacco_id):
        farmer = _farmer(client, sacco_id)
        r = client.post(BASE, json=_payload(farmer["id"], acreage="0"))
        assert r.status_code == 422


class TestGetFarm:
    def test_success(self, client, sacco_id):
        farmer = _farmer(client, sacco_id)
        farm = client.post(BASE, json=_payload(farmer["id"])).json()
        r = client.get(f"{BASE}/{farm['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == farm["id"]

    def test_not_found_returns_404(self, client):
        r = client.get(f"{BASE}/{uuid.uuid4()}")
        assert r.status_code == 404
