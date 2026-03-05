import os
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import HTTPException, Request


AUTH_COOKIE_NAME = "pm_auth"
AUTH_COOKIE_VALUE = "1"
LEGACY_AUTH_SUB = "00000000-0000-0000-0000-000000000001"
LEGACY_AUTH_EMAIL = "user@example.local"


@dataclass(frozen=True)
class AuthenticatedUser:
    sub: str
    email: str | None


def _get_supabase_url() -> str:
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise HTTPException(status_code=500, detail="SUPABASE_URL is not configured")
    return supabase_url.rstrip("/")


def _get_jwks_url() -> str:
    explicit = os.getenv("SUPABASE_JWKS_URL")
    if explicit:
        return explicit
    return f"{_get_supabase_url()}/auth/v1/.well-known/jwks.json"


def _get_expected_issuer() -> str:
    return f"{_get_supabase_url()}/auth/v1"


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    return jwt.PyJWKClient(_get_jwks_url())


def _verify_supabase_token(token: str) -> AuthenticatedUser:
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=_get_expected_issuer(),
            options={"verify_aud": False},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token") from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    email = payload.get("email")
    if email is not None and not isinstance(email, str):
        email = None

    return AuthenticatedUser(sub=subject, email=email)


def require_authenticated_user(request: Request) -> AuthenticatedUser:
    authorization_header = request.headers.get("Authorization", "")
    if authorization_header.startswith("Bearer "):
        token = authorization_header.removeprefix("Bearer ").strip()
        if token:
            return _verify_supabase_token(token)

    if request.cookies.get(AUTH_COOKIE_NAME) == AUTH_COOKIE_VALUE:
        return AuthenticatedUser(sub=LEGACY_AUTH_SUB, email=LEGACY_AUTH_EMAIL)

    raise HTTPException(status_code=401, detail="Authentication required")
