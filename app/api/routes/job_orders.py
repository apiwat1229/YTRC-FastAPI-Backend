from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, require_permission
from app.schemas.job_order import CreateJobOrderDto, UpdateJobOrderDto
from app.services.job_orders_service import JobOrdersService

router = APIRouter(prefix="/job-orders", tags=["Job Orders"])


@router.get("", dependencies=[Depends(require_permission("JOB_ORDERS_READ"))])
async def find_all_orders(db: AsyncSession = Depends(db_session_dependency)):
    return await JobOrdersService(db).find_all()


@router.get("/{order_id}", dependencies=[Depends(require_permission("JOB_ORDERS_READ"))])
async def find_one_order(order_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await JobOrdersService(db).find_one(order_id)


@router.post("", dependencies=[Depends(require_permission("JOB_ORDERS_CREATE"))])
async def create_order(payload: CreateJobOrderDto, db: AsyncSession = Depends(db_session_dependency)):
    return await JobOrdersService(db).create(payload)


@router.patch("/{order_id}", dependencies=[Depends(require_permission("JOB_ORDERS_UPDATE"))])
async def update_order(
    order_id: str,
    payload: UpdateJobOrderDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await JobOrdersService(db).update(order_id, payload)


@router.delete("/{order_id}", dependencies=[Depends(require_permission("JOB_ORDERS_DELETE"))])
async def delete_order(order_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await JobOrdersService(db).remove(order_id)


@router.post("/{order_id}/close", dependencies=[Depends(require_permission("JOB_ORDERS_UPDATE"))])
async def close_job(order_id: str, production_info: dict, db: AsyncSession = Depends(db_session_dependency)):
    return await JobOrdersService(db).close_job(order_id, production_info)
