from datetime import datetime

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency
from app.schemas.pool import PoolCreateDto, PoolItemDto, PoolUpdateDto
from app.services.pools_service import PoolsService

router = APIRouter(prefix="/pools", tags=["Pools"])


@router.get("")
async def list_pools(db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).list_pools()


@router.post("/seed")
async def seed_pools(db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).seed_pools()


@router.get("/{pool_id}")
async def get_pool(pool_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).get_pool(pool_id)


@router.post("")
async def create_pool(payload: PoolCreateDto, db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).create_pool(payload.model_dump(exclude_unset=True))


@router.put("/{pool_id}")
async def update_pool(pool_id: str, payload: PoolUpdateDto, db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).update_pool(pool_id, payload.model_dump(exclude_unset=True))


@router.post("/{pool_id}/items")
async def add_items(pool_id: str, items: list[PoolItemDto], db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).add_items(pool_id, [item.model_dump(exclude_unset=True) for item in items])


@router.delete("/{pool_id}/items/{booking_id}")
async def remove_item(pool_id: str, booking_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).remove_item(pool_id, booking_id)


@router.post("/{pool_id}/close")
async def close_pool(
    pool_id: str,
    close_date: str | None = Body(default=None, embed=True, alias="close_date"),
    db: AsyncSession = Depends(db_session_dependency),
):
    parsed = datetime.fromisoformat(close_date.replace("Z", "+00:00")) if close_date else None
    return await PoolsService(db).close_pool(pool_id, parsed)


@router.post("/{pool_id}/reopen")
async def reopen_pool(pool_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await PoolsService(db).reopen_pool(pool_id)
