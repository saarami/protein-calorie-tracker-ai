from __future__ import annotations

import uuid
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ErrorCodes, http_error
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from typing import NoReturn

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized() -> NoReturn:
    raise http_error(401, ErrorCodes.AUTH_UNAUTHORIZED, "Not authenticated")

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    # No header at all
    if credentials is None:
        _unauthorized()

    # Wrong scheme (not Bearer)
    if credentials.scheme.lower() != "bearer":
        _unauthorized()

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )

        subject = payload.get("sub")
        if subject is None:
            _unauthorized()

        user_id = uuid.UUID(subject)

    except (JWTError, ValueError):
        _unauthorized()

    user = UserRepository(db).get_by_id(user_id)
    if not user:
        _unauthorized()

    return user
