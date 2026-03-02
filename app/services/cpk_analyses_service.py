from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cpk_analysis import CpkAnalysis
from app.schemas.cpk_analysis import CreateCpkAnalysisDto


class CpkAnalysesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: CreateCpkAnalysisDto) -> dict:
        data = payload.model_dump()
        analysis = CpkAnalysis(
            id=str(uuid4()),
            title=data["title"],
            lsl=data["lsl"],
            usl=data["usl"],
            subgroup_size=data["subgroupSize"],
            data_points=data["dataPoints"],
            note=data.get("note"),
            recorded_by=data.get("recordedBy"),
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return self._serialize(analysis)

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(CpkAnalysis).order_by(desc(CpkAnalysis.created_at)))
        return [
            {"id": item.id, "title": item.title, "createdAt": item.created_at} for item in result.scalars().all()
        ]

    async def find_one(self, analysis_id: str) -> dict:
        analysis = await self.db.get(CpkAnalysis, analysis_id)
        if not analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CPK Analysis not found")
        return self._serialize(analysis)

    async def remove(self, analysis_id: str) -> dict:
        analysis = await self.db.get(CpkAnalysis, analysis_id)
        if not analysis:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CPK Analysis not found")
        data = {"id": analysis.id, "title": analysis.title}
        await self.db.delete(analysis)
        await self.db.commit()
        return data

    def _serialize(self, analysis: CpkAnalysis) -> dict:
        return {
            "id": analysis.id,
            "title": analysis.title,
            "lsl": analysis.lsl,
            "usl": analysis.usl,
            "subgroupSize": analysis.subgroup_size,
            "dataPoints": analysis.data_points,
            "note": analysis.note,
            "recordedBy": analysis.recorded_by,
            "createdAt": analysis.created_at,
            "updatedAt": analysis.updated_at,
        }
