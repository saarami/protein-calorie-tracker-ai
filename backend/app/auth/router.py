from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.core.config import settings
from app.core.errors import ErrorCodes, http_error
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_response(user_id: str) -> TokenResponse:
    token = create_access_token(user_id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expires_minutes * 60,
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    repo = UserRepository(db)

    if repo.get_by_email(payload.email):
        raise http_error(409, ErrorCodes.AUTH_EMAIL_ALREADY_EXISTS, "Email already exists")

    user = repo.create(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    repo = UserRepository(db)

    user = repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise http_error(401, ErrorCodes.AUTH_INVALID_CREDENTIALS, "Invalid credentials")

    return _token_response(str(user.id))
