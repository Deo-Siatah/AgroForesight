"""
tests/test_validation_edges.py
Focused validation checks for tricky user input edge cases.
"""

from tests.conftest import sacco_admin_auth_headers


FARMERS = "/api/v1/farmers"


def _payload(sacco_id, **overrides):
    return {
        "sacco_id": str(sacco_id),
        "first_name": "Jane",
        "last_name": "Wanjiku",
        "phone": "+254700000001",
        "national_id": "12345678",
        "login_email": f"farmer-{sacco_id.hex}@agroforesight.local",
        "login_password": "farmer123",
        **overrides,
    }


class TestFarmerInputNormalization:
    def test_phone_with_padding_is_normalized(self, client, sacco_id):
        r = client.post(FARMERS, json=_payload(sacco_id, phone="  +254700000002  "), headers=sacco_admin_auth_headers())
        assert r.status_code == 201
        assert r.json()["phone"] == "+254700000002"

    def test_plus_zero_phone_returns_422(self, client, sacco_id):
        r = client.post(FARMERS, json=_payload(sacco_id, phone="+000000000"), headers=sacco_admin_auth_headers())
        assert r.status_code == 422

    def test_padded_national_id_is_normalized(self, client, sacco_id):
        r = client.post(FARMERS, json=_payload(sacco_id, national_id=" 12345679 "), headers=sacco_admin_auth_headers())
        assert r.status_code == 201
        assert r.json()["national_id"] == "12345679"
