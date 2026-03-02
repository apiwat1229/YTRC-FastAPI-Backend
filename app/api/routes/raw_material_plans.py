from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency
from app.schemas.raw_material_plan import CreateRawMaterialPlanDto
from app.services.raw_material_plans_service import RawMaterialPlansService

router = APIRouter(prefix="/raw-material-plans", tags=["Raw Material Plans"])


@router.post("")
async def create_plan(payload: CreateRawMaterialPlanDto, db: AsyncSession = Depends(db_session_dependency)):
    return await RawMaterialPlansService(db).create(payload)


@router.get("")
async def find_all_plans(db: AsyncSession = Depends(db_session_dependency)):
    return await RawMaterialPlansService(db).find_all()


@router.get("/next-plan-no")
async def generate_next_plan_no(db: AsyncSession = Depends(db_session_dependency)):
    return await RawMaterialPlansService(db).generate_next_plan_no()


@router.get("/{plan_id}")
async def find_one_plan(plan_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await RawMaterialPlansService(db).find_one(plan_id)


@router.patch("/{plan_id}")
async def update_plan(
    plan_id: str,
    payload: CreateRawMaterialPlanDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await RawMaterialPlansService(db).update(plan_id, payload)


@router.delete("/{plan_id}")
async def delete_plan(plan_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await RawMaterialPlansService(db).remove(plan_id)
