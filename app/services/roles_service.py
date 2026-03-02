from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import asc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.user import User
from app.schemas.role import CreateRoleDto, UpdateRoleDto


class RolesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(
            select(Role, func.count(User.id).label("user_count"))
            .outerjoin(User, User.role_id == Role.id)
            .group_by(Role.id)
            .order_by(asc(Role.name))
        )
        rows = result.all()
        return [self._serialize_role(role, user_count) for role, user_count in rows]

    async def find_one(self, role_id: str) -> dict:
        role = await self.db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {role_id} not found")

        users_result = await self.db.execute(select(User).where(User.role_id == role_id))
        users = users_result.scalars().all()
        data = self._serialize_role(role, len(users))
        data["users"] = [
            {
                "id": user.id,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "displayName": user.display_name,
                "avatar": user.avatar,
                "department": user.department,
                "position": user.position,
                "employeeId": user.employee_id,
            }
            for user in users
        ]
        return data

    async def create(self, payload: CreateRoleDto) -> dict:
        role = Role(
            id=str(uuid4()),
            name=payload.name,
            description=payload.description,
            icon=payload.icon,
            color=payload.color,
            permissions=payload.permissions or [],
            is_active=True if payload.isActive is None else payload.isActive,
        )
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return self._serialize_role(role, 0)

    async def update(self, role_id: str, payload: UpdateRoleDto) -> dict:
        role = await self.db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {role_id} not found")

        update_data = payload.model_dump(exclude_unset=True)
        field_map = {"isActive": "is_active"}
        for key, value in update_data.items():
            setattr(role, field_map.get(key, key), value)

        await self.db.commit()
        await self.db.refresh(role)

        count_result = await self.db.execute(select(func.count(User.id)).where(User.role_id == role_id))
        user_count = count_result.scalar_one()
        return self._serialize_role(role, user_count)

    async def remove(self, role_id: str) -> dict:
        role = await self.db.get(Role, role_id)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role with ID {role_id} not found")

        count_result = await self.db.execute(select(func.count(User.id)).where(User.role_id == role_id))
        user_count = count_result.scalar_one()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role with {user_count} assigned users",
            )

        data = self._serialize_role(role, user_count)
        await self.db.delete(role)
        await self.db.commit()
        return data

    def _serialize_role(self, role: Role, user_count: int) -> dict:
        return {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "icon": role.icon,
            "color": role.color,
            "permissions": role.permissions or [],
            "isActive": role.is_active,
            "createdAt": role.created_at,
            "updatedAt": role.updated_at,
            "userCount": user_count,
        }
