from __future__ import annotations

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ErrorCodes, http_error
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _unauthorized():
    raise http_error(401,ErrorCodes.AUTH_UNAUTHORIZED,"Not authenticated",)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
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
    if user is None:
        _unauthorized()

    return user
