from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency
from app.schemas.production_report import CreateProductionReportDto
from app.services.production_reports_service import ProductionReportsService

router = APIRouter(prefix="/production-reports", tags=["Production Reports"])


@router.post("")
async def create_report(payload: CreateProductionReportDto, db: AsyncSession = Depends(db_session_dependency)):
    return await ProductionReportsService(db).create(payload)


@router.get("")
async def find_all_reports(db: AsyncSession = Depends(db_session_dependency)):
    return await ProductionReportsService(db).find_all()


@router.get("/{report_id}")
async def find_one_report(report_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ProductionReportsService(db).find_one(report_id)


@router.patch("/{report_id}")
async def update_report(
    report_id: str,
    payload: CreateProductionReportDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ProductionReportsService(db).update(report_id, payload)


@router.delete("/{report_id}")
async def delete_report(report_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ProductionReportsService(db).remove(report_id)
