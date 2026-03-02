from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency
from app.schemas.shipping_plan import CreateShippingPlanDto
from app.services.shipping_plans_service import ShippingPlansService

router = APIRouter(prefix="/shipping-plans", tags=["Shipping Plans"])


@router.post("")
async def create_plan(payload: CreateShippingPlanDto, db: AsyncSession = Depends(db_session_dependency)):
    return await ShippingPlansService(db).create(payload)


@router.get("")
async def find_all_plans(db: AsyncSession = Depends(db_session_dependency)):
    return await ShippingPlansService(db).find_all()


@router.get("/available-pallets")
async def find_available_pallets(db: AsyncSession = Depends(db_session_dependency)):
    return await ShippingPlansService(db).find_available_pallets()
