from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency
from app.schemas.cpk_analysis import CreateCpkAnalysisDto
from app.services.cpk_analyses_service import CpkAnalysesService

router = APIRouter(prefix="/cpk-analyses", tags=["CPK Analyses"])


@router.post("")
async def create_analysis(payload: CreateCpkAnalysisDto, db: AsyncSession = Depends(db_session_dependency)):
    return await CpkAnalysesService(db).create(payload)


@router.get("")
async def find_all_analyses(db: AsyncSession = Depends(db_session_dependency)):
    return await CpkAnalysesService(db).find_all()


@router.get("/{analysis_id}")
async def find_one_analysis(analysis_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await CpkAnalysesService(db).find_one(analysis_id)


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await CpkAnalysesService(db).remove(analysis_id)
