from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import CreateUserDto, UpdateUserDto


class UsersService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: CreateUserDto) -> dict[str, Any]:
        email_user = await self.find_by_email(payload.email)
        if email_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

        if payload.username:
            username_user = await self.find_by_email_or_username(payload.username)
            if username_user:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already taken")

        user = User(
            id=str(uuid4()),
            email=payload.email,
            username=payload.username,
            password=get_password_hash(payload.password),
            first_name=payload.firstName,
            last_name=payload.lastName,
            display_name=payload.displayName,
            department=payload.department,
            position=payload.position,
            role=payload.role or "staff_1",
            status=payload.status or "ACTIVE",
            avatar=payload.avatar,
            employee_id=payload.employeeId,
            pin_code=get_password_hash(payload.pinCode) if payload.pinCode else None,
            force_change_password=True,
            role_id=payload.role if payload.role else None,
            signature_text=payload.signatureText,
            signature_style=payload.signatureStyle,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return self._serialize_user(user, include_password=False)

    async def create_pending_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        user = User(
            id=str(uuid4()),
            email=payload["email"],
            username=payload["username"],
            password=payload["password"],
            first_name=payload.get("firstName"),
            last_name=payload.get("lastName"),
            status="PENDING",
            force_change_password=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return self._serialize_user(user, include_password=False)

    async def find_all(self) -> list[dict[str, Any]]:
        result = await self.db.execute(select(User).order_by(User.created_at.desc()))
        return [self._serialize_user(row, include_password=False) for row in result.scalars().all()]

    async def find_one(self, user_id: str) -> dict[str, Any]:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
        return self._serialize_user(user, include_password=False)

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return self._serialize_user(user, include_password=True) if user else None

    async def find_by_id_with_password(self, user_id: str) -> dict[str, Any] | None:
        user = await self.db.get(User, user_id)
        return self._serialize_user(user, include_password=True) if user else None

    async def find_by_email_or_username(self, identifier: str) -> dict[str, Any] | None:
        result = await self.db.execute(
            select(User).where(or_(User.email == identifier, User.username == identifier)).limit(1)
        )
        user = result.scalar_one_or_none()
        return self._serialize_user(user, include_password=True) if user else None

    async def find_by_employee_id(self, employee_id: str) -> dict[str, Any] | None:
        result = await self.db.execute(select(User).where(User.employee_id == employee_id).limit(1))
        user = result.scalar_one_or_none()
        return self._serialize_user(user, include_password=False) if user else None

    async def update(self, user_id: str, payload: UpdateUserDto) -> dict[str, Any]:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")

        update_data = payload.model_dump(exclude_unset=True)
        mapping = {
            "firstName": "first_name",
            "lastName": "last_name",
            "displayName": "display_name",
            "employeeId": "employee_id",
            "forceChangePassword": "force_change_password",
            "roleId": "role_id",
            "signatureText": "signature_text",
            "signatureStyle": "signature_style",
        }

        for key, value in update_data.items():
            if key == "password" and value:
                setattr(user, "password", get_password_hash(value))
                continue
            if key == "pinCode" and value:
                setattr(user, "pin_code", get_password_hash(value))
                continue
            target_field = mapping.get(key, key)
            if hasattr(user, target_field):
                setattr(user, target_field, value)

        if payload.role is not None:
            user.role_id = payload.role or None

        try:
            await self.db.commit()
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unique constraint violation") from exc

        await self.db.refresh(user)
        return self._serialize_user(user, include_password=False)

    async def remove(self, user_id: str) -> dict[str, Any]:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")

        data = self._serialize_user(user, include_password=False)
        await self.db.delete(user)
        await self.db.commit()
        return data

    async def update_last_login(self, user_id: str) -> None:
        user = await self.db.get(User, user_id)
        if not user:
            return
        user.last_login_at = datetime.now(UTC)
        await self.db.commit()

    async def update_login_attempts(self, user_id: str, attempts: int, lock: bool = False) -> None:
        user = await self.db.get(User, user_id)
        if not user:
            return
        user.failed_login_attempts = attempts
        if lock:
            user.status = "SUSPENDED"
        await self.db.commit()

    async def unlock_user(self, user_id: str) -> dict[str, Any]:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")

        user.status = "ACTIVE"
        user.failed_login_attempts = 0
        await self.db.commit()
        await self.db.refresh(user)
        return {
            "id": user.id,
            "email": user.email,
            "displayName": user.display_name,
            "status": user.status,
            "failedLoginAttempts": user.failed_login_attempts,
        }

    async def update_avatar(self, user_id: str, avatar_url: str) -> dict[str, Any]:
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {user_id} not found")
        user.avatar = avatar_url
        await self.db.commit()
        return {"id": user.id, "avatar": user.avatar}

    def _serialize_user(self, user: User | None, include_password: bool) -> dict[str, Any] | None:
        if not user:
            return None

        try:
            role_permissions = []
            role_record_data = None
            
            # Safely check for role_record
            try:
                role_record = getattr(user, "role_record", None)
                if role_record and not isinstance(role_record, type):
                    role_permissions = getattr(role_record, "permissions", []) or []
                    role_record_data = {
                        "id": getattr(role_record, "id", None),
                        "name": getattr(role_record, "name", None),
                        "permissions": role_permissions,
                    }
            except Exception as e:
                print(f"Error serializing role_record for user {user.id}: {e}")

            # Safely handle notification groups
            notification_groups = []
            try:
                groups = getattr(user, "notification_groups", [])
                if groups:
                    notification_groups = [
                        {"id": group.id, "name": group.name, "color": group.color, "icon": group.icon}
                        for group in groups
                    ]
            except Exception as e:
                print(f"Error serializing notification_groups for user {user.id}: {e}")

            base = {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "displayName": user.display_name,
                "department": user.department,
                "position": user.position,
                "employeeId": user.employee_id,
                "role": user.role,
                "status": user.status,
                "avatar": user.avatar,
                "createdAt": str(user.created_at) if user.created_at else None,
                "updatedAt": str(user.updated_at) if user.updated_at else None,
                "failedLoginAttempts": getattr(user, "failed_login_attempts", 0),
                "forceChangePassword": getattr(user, "force_change_password", False),
                "signatureText": getattr(user, "signature_text", None),
                "signatureStyle": getattr(user, "signature_style", None),
                "notificationGroups": notification_groups,
                "permissions": role_permissions or getattr(user, "permissions", []) or [],
                "preferences": getattr(user, "preferences", {}),
                "roleRecord": role_record_data,
            }
            if include_password:
                base["password"] = user.password
            return base
        except Exception as e:
            print(f"CRITICAL ERROR in _serialize_user for user {getattr(user, 'id', 'unknown')}: {e}")
            # Return a minimal version if possible to prevent 500
            if user:
                return {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                    "status": user.status,
                    "permissions": [],
                }
            return None
