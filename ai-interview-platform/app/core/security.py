from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from app.core.config import get_settings

TOKEN_TYPE_ACCESS = "access"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{_b64url_encode(salt)}${_b64url_encode(dk)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, dk_b64 = stored.split("$", 1)
        salt = _b64url_decode(salt_b64)
        dk = _b64url_decode(dk_b64)
        new_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return hmac.compare_digest(dk, new_dk)
    except Exception:
        return False


def _get_secret() -> bytes:
    secret = os.getenv("JWT_SECRET")
    if secret:
        return secret.encode("utf-8")
    _ = get_settings()
    return b"dev_secret_change_me"


def _create_signed_token(payload: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig = hmac.new(_get_secret(), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def _decode_signed_token(token: str) -> dict[str, Any] | None:
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected = hmac.new(_get_secret(), signing_input, hashlib.sha256).digest()
        got = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected, got):
            return None

        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        exp = int(payload.get("exp", 0))
        if exp and exp < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def create_access_token(*, sub: str, email: str, role: str, session_id: str, expires_in_seconds: int | None = None) -> str:
    settings = get_settings()
    ttl = int(expires_in_seconds or settings.ACCESS_TOKEN_EXPIRES_SECONDS)
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email,
        "role": role,
        "sid": session_id,
        "typ": TOKEN_TYPE_ACCESS,
        "iat": now,
        "exp": now + ttl,
    }
    return _create_signed_token(payload)


def decode_access_token(token: str) -> dict[str, Any] | None:
    payload = _decode_signed_token(token)
    if not payload:
        return None
    if payload.get("typ") != TOKEN_TYPE_ACCESS:
        return None
    return payload


def create_scoped_token(payload: dict[str, Any], expires_in_seconds: int | None = None) -> str:
    now = int(time.time())
    data = dict(payload)
    data.setdefault("iat", now)
    if expires_in_seconds:
        data["exp"] = now + int(expires_in_seconds)
    return _create_signed_token(data)


def decode_scoped_token(token: str) -> dict[str, Any] | None:
    return _decode_signed_token(token)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
