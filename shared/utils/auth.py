import os
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from jose import jwt
import uuid

KEY_TOKEN_HASHER = os.getenv("KEY_TOKEN_HASHER", "oneverylongandsupersecretpassword")
HASHER_ALGORITHM = os.getenv("HASHER_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1500"))

password_hasher = PasswordHasher(memory_cost=131072, time_cost=3, parallelism=2)
token_hasher = PasswordHasher(memory_cost=65536, time_cost=1, parallelism=1)
fast_hasher = PasswordHasher(memory_cost=16384, time_cost=1, parallelism=1)

class HashError(Exception):
    """Base error for HashUtils."""


class EmptyHashTarget(HashError):
    """Empty input provided."""


class HashMismatch(HashError):
    """Value does not match hash."""


class InvalidHashFormat(HashError):
    """Stored hash is invalid or corrupted."""

def hash_value(hasher: PasswordHasher, value: str) -> str:
    if not value or not value.strip():
        raise EmptyHashTarget("Cannot hash empty string")

    try:
        return hasher.hash(value)
    except Exception as e:
        raise HashError("Hash operation failed") from e


def verify_value(hasher: PasswordHasher, value: str, hashed_value: str) -> None:
    if not value or not value.strip():
        raise EmptyHashTarget("Cannot verify empty string")
    if not hashed_value or not hashed_value.strip():
        raise EmptyHashTarget("Cannot verify empty string")

    try:
        hasher.verify(hashed_value, value)
    except VerifyMismatchError:
        raise HashMismatch("Hash verification failed")
    except VerificationError:
        raise InvalidHashFormat("Unknown or invalid hash format")
    except Exception as e:
        raise HashError("Hash operation failed") from e


def hash_password(password: str) -> str:
    """Hashes a password using the password context."""
    return hash_value(password_hasher, password)


def hash_token(token: str) -> str:
    """Hashes a token using the token context."""
    return hash_value(token_hasher, token)


def hash_string(secret: str) -> str:
    """Hashes a string using the fast context."""
    return hash_value(fast_hasher, secret)


def verify_password(password: str, hashed_password: str) -> None:
    """Verifies a password using the password context."""
    verify_value(password_hasher, password, hashed_password)
    if password_hasher.check_needs_rehash(hashed_password):
        raise HashError("Rehash of password needed.")


def verify_token(token: str, hashed_token: str) -> None:
    """Verifies a token using the token context."""
    verify_value(token_hasher, token, hashed_token)


def verify_string(secret: str, hashed_secret: str) -> None:
    """Verifies a string using the fast context."""
    verify_value(fast_hasher, secret, hashed_secret)

class TokenService:
    def __init__(self, id: uuid.UUID, username: str):
        self.id = id
        self.username = username
    
    def generate_tokens(self):
        """Generates both Access and Refresh JWT tokens"""
        now = datetime.now(timezone.utc)
        access_expires = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = now + timedelta(days=7)

        jti = str(uuid.uuid4())  # Unique ID for refresh token

        access_payload = {
            "sub": str(self.id),
            "username": self.username,
            "exp": access_expires,
            "iat": now,
            "token_type": "access"
        }

        refresh_payload = {
            "sub": str(self.id),
            "username": self.username,
            "exp": refresh_expires,
            "iat": now,
            "jti": jti,
            "token_type": "refresh"
        }

        access_token = jwt.encode(access_payload, KEY_TOKEN_HASHER, algorithm=HASHER_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, KEY_TOKEN_HASHER, algorithm=HASHER_ALGORITHM)

        return access_token, refresh_token
