import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        password_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def _parse_expiration(value: str) -> timedelta:
    if value.endswith("d"):
        return timedelta(days=int(value[:-1]))
    if value.endswith("h"):
        return timedelta(hours=int(value[:-1]))
    if value.endswith("m"):
        return timedelta(minutes=int(value[:-1]))
    return timedelta(days=7)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or _parse_expiration(settings.jwt_expiration)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> tuple[str, str, datetime]:
    """Return (token, jti, expires_at)."""
    jti = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + _parse_expiration(settings.jwt_refresh_expiration)
    to_encode = {**data, "jti": jti, "exp": expires_at, "type": "refresh"}
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return token, jti, expires_at


def create_temporary_token(data: dict, minutes: int = 30) -> str:
    return create_access_token(data, timedelta(minutes=minutes))


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Could not validate token") from exc
