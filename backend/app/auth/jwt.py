from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.core.config import settings


def create_access_token(subject: str) -> str:
    """
    Create a signed JWT access token.

    Payload:
    - sub: user identifier
    - exp: expiration (UTC)
    """
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expires_minutes
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
