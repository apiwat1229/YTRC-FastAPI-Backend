from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.e_signature import CreateESignatureDto, UpdateESignatureDto
from app.services.e_signatures_service import ESignaturesService

router = APIRouter(prefix="/e-signatures", tags=["E-Signatures"])


@router.post("", dependencies=[Depends(get_current_user)])
async def create_signature(payload: CreateESignatureDto, db: AsyncSession = Depends(db_session_dependency)):
    return await ESignaturesService(db).create(payload)


@router.get("", dependencies=[Depends(get_current_user)])
async def find_all_signatures(db: AsyncSession = Depends(db_session_dependency)):
    return await ESignaturesService(db).find_all()


@router.get("/employee/{employee_id}", dependencies=[Depends(get_current_user)])
async def find_by_employee_id(employee_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ESignaturesService(db).find_by_employee_id(employee_id)


@router.get("/employee/{employee_id}/active", dependencies=[Depends(get_current_user)])
async def get_active_by_employee_id(employee_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ESignaturesService(db).get_active_by_employee_id(employee_id)


@router.get("/{signature_id}", dependencies=[Depends(get_current_user)])
async def find_one_signature(signature_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ESignaturesService(db).find_one(signature_id)


@router.patch("/{signature_id}", dependencies=[Depends(get_current_user)])
async def update_signature(
    signature_id: str,
    payload: UpdateESignatureDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ESignaturesService(db).update(signature_id, payload)


@router.delete("/{signature_id}", dependencies=[Depends(get_current_user)])
async def delete_signature(signature_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ESignaturesService(db).remove(signature_id)
