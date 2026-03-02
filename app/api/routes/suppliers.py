from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user, permissions_required
from app.core.permissions import (
    SUPPLIERS_CREATE,
    SUPPLIERS_DELETE,
    SUPPLIERS_DELETE_REQUEST,
    SUPPLIERS_READ,
    SUPPLIERS_UPDATE,
    SUPPLIERS_UPDATE_REQUEST,
)
from app.schemas.approval import CreateApprovalRequestDto
from app.schemas.supplier import CreateSupplierDto, UpdateSupplierDto
from app.services.approvals_service import ApprovalsService
from app.services.suppliers_service import SuppliersService

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("", dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_CREATE))])
async def create_supplier(payload: CreateSupplierDto, db: AsyncSession = Depends(db_session_dependency)):
    return await SuppliersService(db).create(payload)


@router.get("", dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_READ))])
async def find_all_suppliers(
    includeDeleted: str | None = Query(default=None),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await SuppliersService(db).find_all(include_deleted=(includeDeleted == "true"))


@router.get("/{supplier_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_READ))])
async def find_one_supplier(supplier_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await SuppliersService(db).find_one(supplier_id)


@router.patch("/{supplier_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_UPDATE))])
async def update_supplier(
    supplier_id: str,
    payload: UpdateSupplierDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await SuppliersService(db).update(supplier_id, payload)


@router.delete("/{supplier_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_DELETE))])
async def remove_supplier(supplier_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await SuppliersService(db).remove(supplier_id)


@router.post(
    "/{supplier_id}/update-request",
    dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_UPDATE_REQUEST))],
)
async def request_update_supplier(
    supplier_id: str,
    payload: UpdateSupplierDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    current_data = await SuppliersService(db).find_one(supplier_id)
    dto = CreateApprovalRequestDto(
        requestType="SUPPLIER_UPDATE",
        entityType="Supplier",
        entityId=supplier_id,
        sourceApp="SUPPLIER_MANAGEMENT",
        actionType="UPDATE",
        currentData=current_data,
        proposedData=payload.model_dump(exclude_unset=True),
        reason="Request to update supplier information",
        priority="NORMAL",
    )
    return await ApprovalsService(db).create_request(current_user["userId"], dto)


@router.post(
    "/{supplier_id}/delete-request",
    dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_DELETE_REQUEST))],
)
async def request_delete_supplier(
    supplier_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    current_data = await SuppliersService(db).find_one(supplier_id)
    dto = CreateApprovalRequestDto(
        requestType="SUPPLIER_DELETE",
        entityType="Supplier",
        entityId=supplier_id,
        sourceApp="SUPPLIER_MANAGEMENT",
        actionType="DELETE",
        currentData=current_data,
        proposedData=None,
        reason="Request to delete supplier",
        priority="NORMAL",
    )
    return await ApprovalsService(db).create_request(current_user["userId"], dto)


@router.delete("/{supplier_id}/soft", dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_DELETE))])
async def soft_delete_supplier(
    supplier_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await SuppliersService(db).soft_delete(supplier_id, current_user["userId"])


@router.post("/{supplier_id}/restore", dependencies=[Depends(get_current_user), Depends(permissions_required(SUPPLIERS_UPDATE))])
async def restore_supplier(supplier_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await SuppliersService(db).restore(supplier_id)
