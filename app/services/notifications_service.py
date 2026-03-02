from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import String, and_, cast, delete, desc, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.notification_group import NotificationGroup
from app.models.notification_setting import NotificationSetting
from app.models.role import Role
from app.models.user import User
from app.schemas.notification import BroadcastDto, UpdateNotificationSettingDto
from app.schemas.notification_group import (NotificationGroupCreateDto,
                                            NotificationGroupUpdateDto)


class NotificationsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> dict:
        notification = Notification(
            id=str(uuid4()),
            user_id=data["userId"],
            title=data["title"],
            message=data["message"],
            type=data.get("type") or "INFO",
            source_app=data["sourceApp"],
            action_type=data["actionType"],
            entity_id=data.get("entityId"),
            action_url=data.get("actionUrl"),
            metadata_json=data.get("metadata") or {},
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return self._map_to_dto(notification)

    async def find_all(self, user_id: str) -> list[dict]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
        )
        return [self._map_to_dto(item) for item in result.scalars().all()]

    async def find_unread(self, user_id: str) -> list[dict]:
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    cast(Notification.status, String) == "UNREAD"
                )
            )
            .order_by(desc(Notification.created_at))
        )
        return [self._map_to_dto(item) for item in result.scalars().all()]

    async def mark_as_read(self, notification_id: str, user_id: str) -> dict:
        result = await self.db.execute(
            select(Notification).where(and_(Notification.id == notification_id, Notification.user_id == user_id)).limit(1)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        notification.status = "READ"
        await self.db.commit()
        await self.db.refresh(notification)
        return self._map_to_dto(notification)

    async def delete(self, notification_id: str, user_id: str) -> dict:
        result = await self.db.execute(
            select(Notification).where(and_(Notification.id == notification_id, Notification.user_id == user_id)).limit(1)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        data = self._map_to_dto(notification)
        await self.db.delete(notification)
        await self.db.commit()
        return data

    async def mark_all_as_read(self, user_id: str) -> dict:
        result = await self.db.execute(
            update(Notification)
            .where(and_(Notification.user_id == user_id, Notification.status == "UNREAD"))
            .values(status="READ")
        )
        await self.db.commit()
        return {"count": result.rowcount}

    async def broadcast(self, payload: BroadcastDto, sender_id: str | None) -> dict:
        where_conditions = []

        if payload.recipientUsers:
            where_conditions.append(User.id.in_(payload.recipientUsers))

        if payload.recipientRoles:
            roles_result = await self.db.execute(select(Role).where(Role.name.in_(payload.recipientRoles)))
            role_ids = [role.id for role in roles_result.scalars().all()]
            where_conditions.append(or_(User.role.in_(payload.recipientRoles), User.role_id.in_(role_ids)))

        if payload.recipientGroups:
            groups_result = await self.db.execute(
                select(NotificationGroup).where(NotificationGroup.id.in_(payload.recipientGroups))
            )
            groups = groups_result.scalars().all()
            group_user_ids: list[str] = []
            for group in groups:
                await self.db.refresh(group, ["members"])
                group_user_ids.extend([member.id for member in group.members])
            if group_user_ids:
                where_conditions.append(User.id.in_(group_user_ids))

        has_targets = bool(payload.recipientUsers or payload.recipientRoles or payload.recipientGroups)
        if not has_targets:
            return {"count": 0, "message": "No recipients specified."}

        if not where_conditions:
            return {"count": 0, "message": "No matching users found."}

        users_result = await self.db.execute(select(User).where(or_(*where_conditions)))
        users = users_result.scalars().all()
        unique_user_ids = list({user.id for user in users})

        if not unique_user_ids:
            return {"count": 0, "message": "No matching users found."}

        created_count = 0
        for user_id in unique_user_ids:
            self.db.add(
                Notification(
                    id=str(uuid4()),
                    title=payload.title,
                    message=payload.message,
                    type=payload.type or "INFO",
                    user_id=user_id,
                    source_app="ADMIN_BROADCAST",
                    action_type="MANUAL_BROADCAST",
                    action_url=payload.actionUrl,
                    metadata_json={"senderId": sender_id},
                )
            )
            created_count += 1

        await self.db.commit()
        return {"count": created_count, "message": f"Broadcasted to {created_count} users."}

    async def trigger_system_notification(self, source_app: str, action_type: str, payload: dict) -> None:
        try:
            result = await self.db.execute(
                select(NotificationSetting).where(
                    and_(NotificationSetting.source_app == source_app, NotificationSetting.action_type == action_type)
                )
            )
            setting = result.scalar_one_or_none()
            if not setting or not setting.is_active:
                return

            target_user_ids: list[str] = []
            roles = list(setting.recipient_roles or [])
            groups = list(setting.recipient_groups or [])

            if roles:
                role_result = await self.db.execute(select(Role).where(Role.name.in_(roles)))
                role_ids = [row.id for row in role_result.scalars().all()]
                user_result = await self.db.execute(
                    select(User).where(or_(User.role.in_(roles), User.role_id.in_(role_ids)))
                )
                target_user_ids.extend([item.id for item in user_result.scalars().all()])

            if groups:
                group_result = await self.db.execute(select(NotificationGroup).where(NotificationGroup.id.in_(groups)))
                for group in group_result.scalars().all():
                    await self.db.refresh(group, ["members"])
                    target_user_ids.extend([member.id for member in group.members])

            unique_ids = list(set(target_user_ids))
            for user_id in unique_ids:
                await self.create(
                    {
                        "userId": user_id,
                        "title": payload.get("title"),
                        "message": payload.get("message"),
                        "type": "REQUEST" if action_type == "APPROVAL_REQUEST" else "INFO",
                        "sourceApp": source_app,
                        "actionType": action_type,
                        "actionUrl": payload.get("actionUrl"),
                    }
                )
        except Exception:
            return

    async def get_settings(self) -> list[dict]:
        result = await self.db.execute(select(NotificationSetting).order_by(NotificationSetting.source_app.asc()))
        return [self._serialize_setting(item) for item in result.scalars().all()]

    async def update_setting(self, payload: UpdateNotificationSettingDto) -> dict:
        result = await self.db.execute(
            select(NotificationSetting)
            .where(
                and_(
                    NotificationSetting.source_app == payload.sourceApp,
                    NotificationSetting.action_type == payload.actionType,
                )
            )
            .limit(1)
        )
        setting = result.scalar_one_or_none()

        if not setting:
            setting = NotificationSetting(
                id=str(uuid4()),
                source_app=payload.sourceApp,
                action_type=payload.actionType,
                is_active=True if payload.isActive is None else payload.isActive,
                recipient_roles=payload.recipientRoles or [],
                recipient_users=payload.recipientUsers or [],
                recipient_groups=payload.recipientGroups or [],
                channels=payload.channels or ["IN_APP"],
            )
            self.db.add(setting)
        else:
            if payload.isActive is not None:
                setting.is_active = payload.isActive
            if payload.recipientRoles is not None:
                setting.recipient_roles = payload.recipientRoles
            if payload.recipientUsers is not None:
                setting.recipient_users = payload.recipientUsers
            if payload.recipientGroups is not None:
                setting.recipient_groups = payload.recipientGroups
            if payload.channels is not None:
                setting.channels = payload.channels

        await self.db.commit()
        await self.db.refresh(setting)
        return self._serialize_setting(setting)

    async def get_broadcast_history(self) -> list[dict]:
        result = await self.db.execute(
            select(Notification)
            .where(and_(Notification.source_app == "ADMIN_BROADCAST", Notification.action_type == "MANUAL_BROADCAST"))
            .order_by(desc(Notification.created_at))
            .limit(100)
        )
        notifications = result.scalars().all()

        grouped: dict[str, dict] = {}
        for notification in notifications:
            key = (
                f"{notification.title}-{notification.message}-{notification.type}-"
                f"{notification.created_at.isoformat()[:16]}"
            )
            if key not in grouped:
                grouped[key] = {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type,
                    "createdAt": notification.created_at,
                    "recipientCount": 1,
                    "recipientDetails": [],
                }
            else:
                grouped[key]["recipientCount"] += 1

            user = await self.db.get(User, notification.user_id)
            if user and not any(item["id"] == user.id for item in grouped[key]["recipientDetails"]):
                grouped[key]["recipientDetails"].append(
                    {
                        "id": user.id,
                        "username": user.username,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "role": user.role,
                    }
                )

        return list(grouped.values())

    async def delete_broadcast(self, notification_id: str) -> dict:
        target = await self.db.get(Notification, notification_id)
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        min_time = target.created_at - timedelta(seconds=5)
        max_time = target.created_at + timedelta(seconds=5)

        result = await self.db.execute(
            delete(Notification).where(
                and_(
                    Notification.title == target.title,
                    Notification.message == target.message,
                    Notification.type == target.type,
                    Notification.source_app == target.source_app,
                    Notification.action_type == target.action_type,
                    Notification.created_at >= min_time,
                    Notification.created_at <= max_time,
                )
            )
        )
        await self.db.commit()
        count = result.rowcount or 0
        return {"count": count, "message": f"Deleted {count} notifications from history."}

    async def delete_broadcasts(self, ids: list[str]) -> dict:
        total = 0
        for item_id in ids:
            try:
                result = await self.delete_broadcast(item_id)
                total += result.get("count", 0)
            except HTTPException:
                continue
        return {"count": total, "message": f"Deleted {total} notifications from history."}

    async def find_all_groups(self) -> list[dict]:
        result = await self.db.execute(select(NotificationGroup).order_by(NotificationGroup.name.asc()))
        groups = result.scalars().all()
        output = []
        for group in groups:
            await self.db.refresh(group, ["members"])
            output.append(
                {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "icon": group.icon,
                    "color": group.color,
                    "isActive": group.is_active,
                    "members": [
                        {
                            "id": member.id,
                            "firstName": member.first_name,
                            "lastName": member.last_name,
                            "role": member.role,
                        }
                        for member in group.members
                    ],
                }
            )
        return output

    async def create_group(self, payload: NotificationGroupCreateDto) -> dict:
        from app.services.notification_groups_service import \
            NotificationGroupsService

        return await NotificationGroupsService(self.db).create(payload)

    async def update_group(self, group_id: str, payload: NotificationGroupUpdateDto) -> dict:
        from app.services.notification_groups_service import \
            NotificationGroupsService

        return await NotificationGroupsService(self.db).update(group_id, payload)

    async def delete_group(self, group_id: str) -> dict:
        from app.services.notification_groups_service import \
            NotificationGroupsService

        return await NotificationGroupsService(self.db).remove(group_id)

    def _map_to_dto(self, notification: Notification) -> dict:
        return {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "status": notification.status,
            "isRead": notification.status == "READ",
            "userId": notification.user_id,
            "sourceApp": notification.source_app,
            "actionType": notification.action_type,
            "entityId": notification.entity_id,
            "actionUrl": notification.action_url,
            "metadata": notification.metadata_json,
            "approvalRequestId": notification.approval_request_id,
            "approvalStatus": notification.approval_status,
            "createdAt": notification.created_at,
        }

    def _serialize_setting(self, setting: NotificationSetting) -> dict:
        return {
            "id": setting.id,
            "sourceApp": setting.source_app,
            "actionType": setting.action_type,
            "isActive": setting.is_active,
            "recipientRoles": setting.recipient_roles or [],
            "recipientUsers": setting.recipient_users or [],
            "recipientGroups": setting.recipient_groups or [],
            "channels": setting.channels or [],
            "createdAt": setting.created_at,
            "updatedAt": setting.updated_at,
        }
