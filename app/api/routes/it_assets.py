from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.it_asset import CreateITAssetDto, UpdateITAssetDto
from app.services.it_assets_service import ITAssetsService

router = APIRouter(prefix="/it-assets", tags=["IT Assets"])


@router.post("", dependencies=[Depends(get_current_user)])
async def create_asset(payload: CreateITAssetDto, db: AsyncSession = Depends(db_session_dependency)):
    return await ITAssetsService(db).create(payload)


@router.get("", dependencies=[Depends(get_current_user)])
async def find_all_assets(db: AsyncSession = Depends(db_session_dependency)):
    return await ITAssetsService(db).find_all()


@router.get("/{asset_id}", dependencies=[Depends(get_current_user)])
async def find_one_asset(asset_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ITAssetsService(db).find_one(asset_id)


@router.patch("/{asset_id}", dependencies=[Depends(get_current_user)])
async def update_asset(
    asset_id: str,
    payload: UpdateITAssetDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await ITAssetsService(db).update(asset_id, payload)


@router.delete("/{asset_id}", dependencies=[Depends(get_current_user)])
async def delete_asset(asset_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await ITAssetsService(db).remove(asset_id)


@router.post("/{asset_id}/image", dependencies=[Depends(get_current_user)])
async def upload_image(
    asset_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(db_session_dependency),
):
    import os
    from pathlib import Path
    import secrets

    upload_dir = Path("uploads/it-asset")
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{secrets.token_hex(16)}{ext}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return await ITAssetsService(db).update_image(asset_id, f"/uploads/it-asset/{filename}")
