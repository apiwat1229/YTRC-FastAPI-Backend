from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.notification_group import NotificationGroupCreateDto, NotificationGroupUpdateDto
from app.schemas.notification import BroadcastDto, DeleteBroadcastsDto, UpdateNotificationSettingDto
from app.services.notifications_service import NotificationsService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", dependencies=[Depends(get_current_user)])
async def find_all(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).find_all(current_user["userId"])


@router.get("/unread", dependencies=[Depends(get_current_user)])
async def find_unread(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).find_unread(current_user["userId"])


@router.put("/{notification_id}/read", dependencies=[Depends(get_current_user)])
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await NotificationsService(db).mark_as_read(notification_id, current_user["userId"])


@router.delete("/{notification_id}", dependencies=[Depends(get_current_user)])
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await NotificationsService(db).delete(notification_id, current_user["userId"])


@router.put("/read-all", dependencies=[Depends(get_current_user)])
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await NotificationsService(db).mark_all_as_read(current_user["userId"])


@router.get("/settings", dependencies=[Depends(get_current_user)])
async def get_settings(db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).get_settings()


@router.post("/broadcast", dependencies=[Depends(get_current_user)])
async def broadcast(
    payload: BroadcastDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await NotificationsService(db).broadcast(payload, current_user.get("userId"))


@router.get("/history", dependencies=[Depends(get_current_user)])
async def get_broadcast_history(db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).get_broadcast_history()


@router.put("/settings", dependencies=[Depends(get_current_user)])
async def update_setting(payload: UpdateNotificationSettingDto, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).update_setting(payload)


@router.get("/groups", dependencies=[Depends(get_current_user)])
async def get_groups(db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).find_all_groups()


@router.post("/groups", dependencies=[Depends(get_current_user)])
async def create_group(payload: NotificationGroupCreateDto, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).create_group(payload)


@router.put("/groups/{group_id}", dependencies=[Depends(get_current_user)])
async def update_group(
    group_id: str,
    payload: NotificationGroupUpdateDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await NotificationsService(db).update_group(group_id, payload)


@router.delete("/groups/{group_id}", dependencies=[Depends(get_current_user)])
async def delete_group(group_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).delete_group(group_id)


@router.delete("/broadcast/{notification_id}", dependencies=[Depends(get_current_user)])
async def delete_broadcast(notification_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).delete_broadcast(notification_id)


@router.delete("/broadcast", dependencies=[Depends(get_current_user)])
async def delete_broadcasts(payload: DeleteBroadcastsDto, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationsService(db).delete_broadcasts(payload.ids)
