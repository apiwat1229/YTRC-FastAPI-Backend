from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency
from app.models.address import District, Province, Subdistrict
from app.models.rubber_type import RubberType

router = APIRouter(prefix="/master", tags=["Master Data"])


@router.get("/provinces")
async def get_provinces(db: AsyncSession = Depends(db_session_dependency)):
    result = await db.execute(select(Province).order_by(Province.name_th.asc()))
    provinces = result.scalars().all()
    return [
        {"id": p.id, "code": p.code, "name_th": p.name_th, "name_en": p.name_en}
        for p in provinces
    ]


@router.get("/provinces/{province_id}/districts")
async def get_districts(province_id: int, db: AsyncSession = Depends(db_session_dependency)):
    result = await db.execute(
        select(District)
        .where(District.province_id == province_id)
        .order_by(District.name_th.asc())
    )
    districts = result.scalars().all()
    return [
        {"id": d.id, "code": d.code, "name_th": d.name_th, "name_en": d.name_en}
        for d in districts
    ]


@router.get("/districts/{district_id}/subdistricts")
async def get_subdistricts(district_id: int, db: AsyncSession = Depends(db_session_dependency)):
    result = await db.execute(
        select(Subdistrict)
        .where(Subdistrict.district_id == district_id)
        .order_by(Subdistrict.name_th.asc())
    )
    subdistricts = result.scalars().all()
    return [
        {
            "id": s.id,
            "code": s.code,
            "name_th": s.name_th,
            "name_en": s.name_en,
            "zip_code": s.zip_code,
        }
        for s in subdistricts
    ]


@router.get("/rubber-types")
async def get_rubber_types(db: AsyncSession = Depends(db_session_dependency)):
    result = await db.execute(select(RubberType).where(RubberType.deleted_at.is_(None)))
    r_types = result.scalars().all()
    return [
        {
            "id": rt.id,
            "code": rt.code,
            "name": rt.name,
            "description": rt.description,
            "category": rt.category,
        }
        for rt in r_types
    ]
