from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_temporary_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.schemas.auth import LoginDto, RegisterDto, SignupDto
from app.schemas.user import CreateUserDto, UpdateUserDto
from app.services.notifications_service import NotificationsService
from app.services.refresh_tokens_service import RefreshTokensService
from app.services.users_service import UsersService


class AuthService:
    def __init__(
        self,
        users_service: UsersService,
        notifications_service: NotificationsService,
        refresh_tokens_service: RefreshTokensService,
    ):
        self.users_service = users_service
        self.notifications = notifications_service
        self.refresh_tokens = refresh_tokens_service

    async def login(self, payload: LoginDto) -> dict[str, Any]:
        identifier = payload.email or payload.username
        if not identifier:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or Username is required",
            )

        user = await self.users_service.find_by_email_or_username(identifier)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        if user.get("status") == "SUSPENDED":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is locked. Please contact admin.",
            )

        if not verify_password(payload.password, user["password"]):
            attempts = (user.get("failedLoginAttempts") or 0) + 1
            should_lock = attempts >= 5
            await self.users_service.update_login_attempts(
                user["id"], attempts, should_lock
            )

            if should_lock:
                await self.notifications.trigger_system_notification(
                    "Auth",
                    "ACCOUNT_LOCKED",
                    {
                        "title": f"Account Locked: {user.get('displayName') or user.get('username')}",
                        "message": f"User account {user['email']} has been locked due to too many failed login attempts.",
                        "actionUrl": f"/admin/users?id={user['id']}",
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account has been locked due to multiple failed login attempts. Please contact IT support.",
                )

            remaining = 5 - attempts
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Password incorrect. {remaining} attempts remaining.",
            )

        if user.get("failedLoginAttempts", 0) > 0:
            await self.users_service.update_login_attempts(user["id"], 0)

        if user.get("forceChangePassword"):
            temp_token = create_temporary_token(
                {"sub": user["id"], "email": user["email"], "scope": "CHANGE_PASSWORD"},
                minutes=30,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "MUST_CHANGE_PASSWORD",
                    "tempToken": temp_token,
                    "message": "You must change your password to continue.",
                },
            )

        await self.users_service.update_last_login(user["id"])
        permissions = (
            (user.get("roleRecord") or {}).get("permissions")
            or user.get("permissions")
            or []
        )

        token_payload = {
            "email": user["email"],
            "sub": user["id"],
            "role": user.get("role"),
            "username": user.get("username"),
            "displayName": user.get("displayName"),
            "permissions": permissions,
            "department": user.get("department"),
        }

        refresh_token, jti, expires_at = create_refresh_token({"sub": user["id"]})
        await self.refresh_tokens.store(jti, user["id"], refresh_token, expires_at)

        return {
            "accessToken": create_access_token(token_payload),
            "refreshToken": refresh_token,
            "user": _safe_user(user, permissions),
        }

    async def register(self, payload: RegisterDto) -> dict[str, Any]:
        user = await self.users_service.create(
            CreateUserDto(
                email=payload.email,
                password=payload.password,
                username=payload.username,
                firstName=payload.firstName,
                lastName=payload.lastName,
            )
        )

        permissions = (
            (user.get("roleRecord") or {}).get("permissions")
            or user.get("permissions")
            or []
        )
        token_payload = {
            "email": user["email"],
            "sub": user["id"],
            "role": user.get("role"),
            "username": user.get("username"),
            "displayName": user.get("displayName"),
            "permissions": permissions,
        }

        refresh_token, jti, expires_at = create_refresh_token({"sub": user["id"]})
        await self.refresh_tokens.store(jti, user["id"], refresh_token, expires_at)

        return {
            "accessToken": create_access_token(token_payload),
            "refreshToken": refresh_token,
            "user": _safe_user(user, permissions),
        }

    async def signup(self, payload: SignupDto) -> dict[str, Any]:
        existing_email = await self.users_service.find_by_email_or_username(
            payload.email
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        existing_username = await self.users_service.find_by_email_or_username(
            payload.username
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
            )

        user = await self.users_service.create_pending_user(
            {
                "email": payload.email,
                "username": payload.username,
                "firstName": payload.firstName,
                "lastName": payload.lastName,
                "password": get_password_hash(payload.password),
            }
        )
        return {
            "message": "Account created successfully. Please wait for admin approval.",
            "userId": user["id"],
        }

    async def refresh(self, refresh_token: str) -> dict[str, Any]:
        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            ) from exc

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        if not await self.refresh_tokens.verify(jti, refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or expired",
            )

        # Rotate: revoke old, issue new
        await self.refresh_tokens.revoke(jti)

        user = await self.users_service.find_one(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        if user.get("status") == "SUSPENDED":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is suspended"
            )

        permissions = (
            (user.get("roleRecord") or {}).get("permissions")
            or user.get("permissions")
            or []
        )
        token_payload = {
            "email": user["email"],
            "sub": user["id"],
            "role": user.get("role"),
            "username": user.get("username"),
            "displayName": user.get("displayName"),
            "permissions": permissions,
            "department": user.get("department"),
        }

        new_refresh_token, new_jti, expires_at = create_refresh_token(
            {"sub": user["id"]}
        )
        await self.refresh_tokens.store(
            new_jti, user["id"], new_refresh_token, expires_at
        )

        return {
            "accessToken": create_access_token(token_payload),
            "refreshToken": new_refresh_token,
        }

    async def logout(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                await self.refresh_tokens.revoke(jti)
        except ValueError:
            pass  # Token already invalid — treat as success
        return {"message": "Logged out successfully"}

    async def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> dict[str, Any]:
        user = await self.users_service.find_by_id_with_password(user_id)
        if not user or not user.get("password"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        if not verify_password(old_password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Old password is incorrect.",
            )

        await self.users_service.update(
            user_id,
            UpdateUserDto(password=new_password, forceChangePassword=False),
        )
        return {"message": "Password changed successfully"}


def _to_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()
    return str(value)


# Fields that must never be returned to clients
_SENSITIVE_FIELDS = frozenset({"password", "pinCode"})


def _safe_user(user: dict[str, Any], permissions: list) -> dict[str, Any]:
    """Return a client-safe user dict with sensitive fields excluded."""
    return {
        k: v
        for k, v in {
            **user,
            "permissions": permissions,
            "createdAt": _to_iso(user.get("createdAt")),
            "updatedAt": _to_iso(user.get("updatedAt")),
        }.items()
        if k not in _SENSITIVE_FIELDS
    }
