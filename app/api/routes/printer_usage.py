from fastapi import APIRouter, Depends

from app.core.deps import get_current_user

router = APIRouter(prefix="/printer-usage", tags=["Printer Usage"])


@router.get("/departments", dependencies=[Depends(get_current_user)])
async def get_departments():
    return []


@router.post("/departments", dependencies=[Depends(get_current_user)])
async def create_department(data: dict):
    return {"message": "Department created - to be implemented"}


@router.put("/departments/{department_id}", dependencies=[Depends(get_current_user)])
async def update_department(department_id: str, data: dict):
    return {"message": "Department updated - to be implemented"}


@router.delete("/departments/{department_id}", dependencies=[Depends(get_current_user)])
async def delete_department(department_id: str):
    return {"message": "Department deleted - to be implemented"}


@router.get("/mappings", dependencies=[Depends(get_current_user)])
async def get_mappings():
    return []


@router.post("/mappings", dependencies=[Depends(get_current_user)])
async def upsert_mapping(data: dict):
    return {"message": "Mapping upserted - to be implemented"}


@router.post("/records", dependencies=[Depends(get_current_user)])
async def save_usage_records(records: list[dict]):
    return {"message": f"Saved {len(records)} records - to be implemented"}


@router.get("/history", dependencies=[Depends(get_current_user)])
async def get_history():
    return []


@router.delete("/history/{period}", dependencies=[Depends(get_current_user)])
async def delete_period(period: str):
    return {"message": f"Period {period} deleted - to be implemented"}
