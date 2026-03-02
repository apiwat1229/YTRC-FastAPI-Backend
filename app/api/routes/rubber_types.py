from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user, permissions_required
from app.core.permissions import (
    RUBBER_TYPES_CREATE,
    RUBBER_TYPES_DELETE,
    RUBBER_TYPES_DELETE_REQUEST,
    RUBBER_TYPES_READ,
    RUBBER_TYPES_UPDATE,
    RUBBER_TYPES_UPDATE_REQUEST,
)
from app.schemas.approval import CreateApprovalRequestDto
from app.schemas.rubber_type import CreateRubberTypeDto, UpdateRubberTypeDto
from app.services.approvals_service import ApprovalsService
from app.services.rubber_types_service import RubberTypesService

router = APIRouter(prefix="/rubber-types", tags=["Rubber Types"])


@router.post("", dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_CREATE))])
async def create_rubber_type(payload: CreateRubberTypeDto, db: AsyncSession = Depends(db_session_dependency)):
    return await RubberTypesService(db).create(payload)


@router.get("", dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_READ))])
async def find_all_rubber_types(
    includeDeleted: str | None = Query(default=None),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await RubberTypesService(db).find_all(include_deleted=(includeDeleted == "true"))


@router.get("/{rubber_type_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_READ))])
async def find_one_rubber_type(rubber_type_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await RubberTypesService(db).find_one(rubber_type_id)


@router.patch("/{rubber_type_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_UPDATE))])
async def update_rubber_type(
    rubber_type_id: str,
    payload: UpdateRubberTypeDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await RubberTypesService(db).update(rubber_type_id, payload)


@router.delete("/{rubber_type_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_DELETE))])
async def remove_rubber_type(rubber_type_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await RubberTypesService(db).remove(rubber_type_id)


@router.post(
    "/{rubber_type_id}/update-request",
    dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_UPDATE_REQUEST))],
)
async def request_update_rubber_type(
    rubber_type_id: str,
    payload: UpdateRubberTypeDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    current_data = await RubberTypesService(db).find_one(rubber_type_id)
    dto = CreateApprovalRequestDto(
        requestType="RUBBER_TYPE_UPDATE",
        entityType="RubberType",
        entityId=rubber_type_id,
        sourceApp="RUBBER_TYPE_MANAGEMENT",
        actionType="UPDATE",
        currentData=current_data,
        proposedData=payload.model_dump(exclude_unset=True),
        reason="Request to update rubber type information",
        priority="NORMAL",
    )
    return await ApprovalsService(db).create_request(current_user["userId"], dto)


@router.post(
    "/{rubber_type_id}/delete-request",
    dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_DELETE_REQUEST))],
)
async def request_delete_rubber_type(
    rubber_type_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    current_data = await RubberTypesService(db).find_one(rubber_type_id)
    dto = CreateApprovalRequestDto(
        requestType="RUBBER_TYPE_DELETE",
        entityType="RubberType",
        entityId=rubber_type_id,
        sourceApp="RUBBER_TYPE_MANAGEMENT",
        actionType="DELETE",
        currentData=current_data,
        proposedData=None,
        reason="Request to delete rubber type",
        priority="NORMAL",
    )
    return await ApprovalsService(db).create_request(current_user["userId"], dto)


@router.delete("/{rubber_type_id}/soft", dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_DELETE))])
async def soft_delete_rubber_type(
    rubber_type_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await RubberTypesService(db).soft_delete(rubber_type_id, current_user["userId"])


@router.post("/{rubber_type_id}/restore", dependencies=[Depends(get_current_user), Depends(permissions_required(RUBBER_TYPES_UPDATE))])
async def restore_rubber_type(rubber_type_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await RubberTypesService(db).restore(rubber_type_id)
