"""
tests/test_auth.py

POST /api/v1/auth/login
GET  /api/v1/auth/me
"""
from __future__ import annotations

import httpx

BASE = "/api/v1/auth"

# Seeded admin from api.md
ADMIN_EMAIL = "admin26@gmail.com"
ADMIN_PASSWORD = "admin26"


class TestLogin:
    def test_valid_credentials_return_token(self):
        r = httpx.post(f"http://127.0.0.1:8000{BASE}/login",
                       json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert "user" in body
        assert body["user"]["role"] == "admin"

    def test_wrong_password_returns_401(self):
        r = httpx.post(f"http://127.0.0.1:8000{BASE}/login",
                       json={"email": ADMIN_EMAIL, "password": "wrongpassword"}, timeout=10)
        assert r.status_code == 401

    def test_unknown_email_returns_401(self):
        r = httpx.post(f"http://127.0.0.1:8000{BASE}/login",
                       json={"email": "nobody@nowhere.test", "password": "irrelevant"}, timeout=10)
        assert r.status_code == 401

    def test_empty_password_returns_422(self):
        r = httpx.post(f"http://127.0.0.1:8000{BASE}/login",
                       json={"email": ADMIN_EMAIL, "password": ""}, timeout=10)
        assert r.status_code == 422

    def test_empty_email_returns_422(self):
        r = httpx.post(f"http://127.0.0.1:8000{BASE}/login",
                       json={"email": "", "password": ADMIN_PASSWORD}, timeout=10)
        assert r.status_code == 422

    def test_missing_body_returns_422(self):
        r = httpx.post(f"http://127.0.0.1:8000{BASE}/login", timeout=10)
        assert r.status_code == 422


class TestMe:
    def test_valid_token_returns_user(self, admin_token):
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/me",
                      headers={"Authorization": f"Bearer {admin_token}"}, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert body["email"] == ADMIN_EMAIL
        assert body["role"] == "admin"
        assert "id" in body

    def test_no_token_returns_401(self):
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/me", timeout=10)
        assert r.status_code == 401

    def test_malformed_token_returns_401(self):
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/me",
                      headers={"Authorization": "Bearer not.a.real.jwt"}, timeout=10)
        assert r.status_code == 401

    def test_wrong_scheme_returns_401(self):
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/me",
                      headers={"Authorization": "Basic dXNlcjpwYXNz"}, timeout=10)
        assert r.status_code == 401

    def test_sacco_admin_me_returns_sacco_id(self, sacco_admin_token, sacco_id):
        r = httpx.get(f"http://127.0.0.1:8000{BASE}/me",
                      headers={"Authorization": f"Bearer {sacco_admin_token}"}, timeout=10)
        assert r.status_code == 200
        body = r.json()
        assert body["role"] == "sacco_admin"
        assert body["sacco_id"] == str(sacco_id)
