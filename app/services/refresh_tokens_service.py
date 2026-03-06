import hashlib
from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class RefreshTokensService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def store(
        self, jti: str, user_id: str, token: str, expires_at: datetime
    ) -> None:
        record = RefreshToken(
            id=jti,
            user_id=user_id,
            token_hash=_hash_token(token),
            expires_at=expires_at,
        )
        self.db.add(record)
        await self.db.commit()

    async def verify(self, jti: str, token: str) -> bool:
        """Return True if the token is valid (exists, not revoked, not expired)."""
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.id == jti)
        )
        record = result.scalar_one_or_none()
        if not record:
            return False
        if record.is_revoked:
            return False
        if record.token_hash != _hash_token(token):
            return False
        if record.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            return False
        return True

    async def revoke(self, jti: str) -> None:
        await self.db.execute(
            update(RefreshToken).where(RefreshToken.id == jti).values(is_revoked=True)
        )
        await self.db.commit()

    async def revoke_all_for_user(self, user_id: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id, RefreshToken.is_revoked == False
            )  # noqa: E712
            .values(is_revoked=True)
        )
        await self.db.commit()

    async def cleanup_expired(self) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC))
        )
        await self.db.commit()
