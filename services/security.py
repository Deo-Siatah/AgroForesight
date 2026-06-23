"""
services/security.py
Local password hashing and JWT access token helpers.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt


ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored: str) -> bool:
    if stored.startswith("pbkdf2_sha256$"):
        _, iterations, salt_b64, digest_b64 = stored.split("$", 3)
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(actual, expected)

    return hmac.compare_digest(password, stored)


def create_access_token(payload: dict[str, str], secret: str, ttl_minutes: int) -> str:
    data = dict(payload)
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    data["iat"] = datetime.now(timezone.utc)
    data["type"] = "access"
    return jwt.encode(data, secret, algorithm="HS256")


def decode_access_token(token: str, secret: str) -> dict[str, str]:
    data = jwt.decode(token, secret, algorithms=["HS256"])
    if data.get("type") != "access":
        raise ValueError("Invalid token type")
    return data