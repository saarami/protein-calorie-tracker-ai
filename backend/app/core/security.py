from __future__ import annotations

import hashlib

from passlib.context import CryptContext

# bcrypt has a hard 72-byte input limit.
# For longer passwords we pre-hash with SHA-256 (common, safe approach).
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_for_bcrypt(password: str) -> str:
    """
    Normalize password input to be safe for bcrypt.
    If the UTF-8 byte length exceeds 72 bytes, hash first with SHA-256.
    """
    password_bytes = password.encode("utf-8")
    if len(password_bytes) <= 72:
        return password

    return hashlib.sha256(password_bytes).hexdigest()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt (with pre-hash if needed).
    """
    normalized = _normalize_for_bcrypt(password)
    return _pwd_context.hash(normalized)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.
    """
    normalized = _normalize_for_bcrypt(password)
    return _pwd_context.verify(normalized, hashed_password)
