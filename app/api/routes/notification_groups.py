from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user, permissions_required
from app.core.permissions import NOTIFICATIONS_CREATE, NOTIFICATIONS_DELETE, NOTIFICATIONS_READ
from app.schemas.notification_group import (
    NotificationGroupAddMembersDto,
    NotificationGroupCreateDto,
    NotificationGroupUpdateDto,
)
from app.services.notification_groups_service import NotificationGroupsService

router = APIRouter(prefix="/notification-groups", tags=["Notification Groups"])


@router.post("", dependencies=[Depends(get_current_user), Depends(permissions_required(NOTIFICATIONS_CREATE))])
async def create_group(payload: NotificationGroupCreateDto, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationGroupsService(db).create(payload)


@router.get("", dependencies=[Depends(get_current_user), Depends(permissions_required(NOTIFICATIONS_READ))])
async def find_all_groups(db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationGroupsService(db).find_all()


@router.get("/{group_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(NOTIFICATIONS_READ))])
async def find_one_group(group_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationGroupsService(db).find_one(group_id)


@router.patch("/{group_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(NOTIFICATIONS_CREATE))])
async def update_group(
    group_id: str,
    payload: NotificationGroupUpdateDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await NotificationGroupsService(db).update(group_id, payload)


@router.delete("/{group_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(NOTIFICATIONS_DELETE))])
async def remove_group(group_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationGroupsService(db).remove(group_id)


@router.post("/{group_id}/members", dependencies=[Depends(get_current_user), Depends(permissions_required(NOTIFICATIONS_CREATE))])
async def add_members(
    group_id: str,
    payload: NotificationGroupAddMembersDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await NotificationGroupsService(db).add_members(group_id, payload.userIds)


@router.delete(
    "/{group_id}/members/{user_id}",
    dependencies=[Depends(get_current_user), Depends(permissions_required(NOTIFICATIONS_DELETE))],
)
async def remove_member(group_id: str, user_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await NotificationGroupsService(db).remove_member(group_id, user_id)
