from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user, permissions_required
from app.core.permissions import APPROVALS_APPROVE, APPROVALS_VIEW
from app.schemas.approval import (
    ApproveDto,
    CancelDto,
    CreateApprovalRequestDto,
    RejectDto,
    ReturnDto,
    VoidDto,
)
from app.services.approvals_service import ApprovalsService

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.post("", dependencies=[Depends(get_current_user)])
async def create_request(
    payload: CreateApprovalRequestDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).create_request(current_user["userId"], payload)


@router.get("", dependencies=[Depends(get_current_user), Depends(permissions_required(APPROVALS_VIEW))])
async def find_all(
    status: str | None = Query(default=None),
    entityType: str | None = Query(default=None),
    includeDeleted: str | None = Query(default=None),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).find_all(status, entityType, includeDeleted == "true")


@router.get("/my", dependencies=[Depends(get_current_user)])
async def find_my_requests(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(db_session_dependency)):
    return await ApprovalsService(db).find_my_requests(current_user["userId"])


@router.get("/{request_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(APPROVALS_VIEW))])
async def find_one(request_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ApprovalsService(db).find_one(request_id)


@router.get("/{request_id}/history", dependencies=[Depends(get_current_user)])
async def get_history(request_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ApprovalsService(db).get_history(request_id)


@router.put("/{request_id}/approve", dependencies=[Depends(get_current_user), Depends(permissions_required(APPROVALS_APPROVE))])
async def approve(
    request_id: str,
    payload: ApproveDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).approve(request_id, current_user["userId"], payload)


@router.put("/{request_id}/reject", dependencies=[Depends(get_current_user), Depends(permissions_required(APPROVALS_APPROVE))])
async def reject(
    request_id: str,
    payload: RejectDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).reject(request_id, current_user["userId"], payload)


@router.put("/{request_id}/return", dependencies=[Depends(get_current_user), Depends(permissions_required(APPROVALS_APPROVE))])
async def return_for_modification(
    request_id: str,
    payload: ReturnDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).return_for_modification(request_id, current_user["userId"], payload)


@router.put("/{request_id}/cancel", dependencies=[Depends(get_current_user)])
async def cancel(
    request_id: str,
    payload: CancelDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).cancel(request_id, current_user["userId"], payload)


@router.put("/{request_id}/void", dependencies=[Depends(get_current_user), Depends(permissions_required(APPROVALS_APPROVE))])
async def void_request(
    request_id: str,
    payload: VoidDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).void(request_id, current_user["userId"], payload)


@router.delete("/{request_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(APPROVALS_APPROVE))])
async def soft_delete(
    request_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ApprovalsService(db).soft_delete(request_id, current_user["userId"])
