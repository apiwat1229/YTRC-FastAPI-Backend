from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_group import NotificationGroup
from app.models.user import User
from app.schemas.notification_group import NotificationGroupCreateDto, NotificationGroupUpdateDto


class NotificationGroupsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: NotificationGroupCreateDto) -> dict:
        group = NotificationGroup(
            id=str(uuid4()),
            name=payload.name,
            description=payload.description,
            icon=payload.icon,
            color=payload.color,
        )

        if payload.memberIds:
            users = await self._load_users(payload.memberIds)
            group.members = users

        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return self._serialize_group(group, include_count=False)

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(NotificationGroup).order_by(desc(NotificationGroup.created_at)))
        groups = result.scalars().all()
        output = []
        for group in groups:
            await self.db.refresh(group, ["members"])
            output.append(self._serialize_group(group, include_count=True))
        return output

    async def find_one(self, group_id: str) -> dict:
        group = await self.db.get(NotificationGroup, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        await self.db.refresh(group, ["members"])
        return self._serialize_group(group, include_count=False)

    async def update(self, group_id: str, payload: NotificationGroupUpdateDto) -> dict:
        group = await self.db.get(NotificationGroup, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        update_data = payload.model_dump(exclude_unset=True)
        field_map = {"isActive": "is_active"}
        for key, value in update_data.items():
            if key == "memberIds":
                continue
            setattr(group, field_map.get(key, key), value)

        if payload.memberIds is not None:
            group.members = await self._load_users(payload.memberIds)

        await self.db.commit()
        await self.db.refresh(group)
        await self.db.refresh(group, ["members"])
        return self._serialize_group(group, include_count=False)

    async def remove(self, group_id: str) -> dict:
        group = await self.db.get(NotificationGroup, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        await self.db.refresh(group, ["members"])
        data = self._serialize_group(group, include_count=False)
        await self.db.delete(group)
        await self.db.commit()
        return data

    async def add_members(self, group_id: str, user_ids: list[str]) -> dict:
        group = await self.db.get(NotificationGroup, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        await self.db.refresh(group, ["members"])
        existing_ids = {member.id for member in group.members}
        users = await self._load_users([user_id for user_id in user_ids if user_id not in existing_ids])
        group.members.extend(users)

        await self.db.commit()
        await self.db.refresh(group)
        await self.db.refresh(group, ["members"])
        return self._serialize_group(group, include_count=False)

    async def remove_member(self, group_id: str, user_id: str) -> dict:
        group = await self.db.get(NotificationGroup, group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        await self.db.refresh(group, ["members"])
        group.members = [member for member in group.members if member.id != user_id]
        await self.db.commit()
        await self.db.refresh(group)
        await self.db.refresh(group, ["members"])
        return self._serialize_group(group, include_count=False)

    async def get_group_members(self, group_name: str) -> list[dict]:
        result = await self.db.execute(select(NotificationGroup).where(NotificationGroup.name == group_name).limit(1))
        group = result.scalar_one_or_none()
        if not group:
            return []
        await self.db.refresh(group, ["members"])
        return [
            {
                "id": member.id,
                "email": member.email,
                "displayName": member.display_name,
                "role": member.role,
            }
            for member in group.members
        ]

    async def _load_users(self, user_ids: list[str]) -> list[User]:
        if not user_ids:
            return []
        result = await self.db.execute(select(User).where(User.id.in_(user_ids)))
        return result.scalars().all()

    def _serialize_group(self, group: NotificationGroup, include_count: bool) -> dict:
        members = [
            {
                "id": member.id,
                "firstName": member.first_name,
                "lastName": member.last_name,
                "email": member.email,
                "avatar": member.avatar,
                "role": member.role,
            }
            for member in group.members
        ]
        base = {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "icon": group.icon,
            "color": group.color,
            "isActive": group.is_active,
            "members": members,
            "createdAt": group.created_at,
            "updatedAt": group.updated_at,
        }
        if include_count:
            base["_count"] = {"members": len(members)}
        return base
