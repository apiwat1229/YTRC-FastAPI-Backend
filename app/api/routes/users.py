import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user, permissions_required
from app.schemas.user import CreateUserDto, UpdateUserDto
from app.services.users_service import UsersService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", dependencies=[Depends(get_current_user), Depends(permissions_required("users:create"))])
async def create_user(payload: CreateUserDto, db: AsyncSession = Depends(db_session_dependency)):
    service = UsersService(db)
    return await service.create(payload)


@router.get("", dependencies=[Depends(get_current_user)])
async def find_all_users(db: AsyncSession = Depends(db_session_dependency)):
    service = UsersService(db)
    return await service.find_all()


@router.get("/employee/{employeeId}/exists", dependencies=[Depends(get_current_user)])
async def employee_exists(employeeId: str, db: AsyncSession = Depends(db_session_dependency)):
    service = UsersService(db)
    user = await service.find_by_employee_id(employeeId)
    return {"exists": bool(user), "userId": user.get("id") if user else None, "_v": 2}


@router.get("/{user_id}", dependencies=[Depends(get_current_user)])
async def find_user(user_id: str, db: AsyncSession = Depends(db_session_dependency)):
    service = UsersService(db)
    return await service.find_one(user_id)


@router.patch("/{user_id}", dependencies=[Depends(get_current_user), Depends(permissions_required("users:update"))])
async def update_user(user_id: str, payload: UpdateUserDto, db: AsyncSession = Depends(db_session_dependency)):
    service = UsersService(db)
    return await service.update(user_id, payload)


@router.delete("/{user_id}", dependencies=[Depends(get_current_user), Depends(permissions_required("users:delete"))])
async def delete_user(user_id: str, db: AsyncSession = Depends(db_session_dependency)):
    service = UsersService(db)
    return await service.remove(user_id)


@router.patch("/{user_id}/unlock", dependencies=[Depends(get_current_user), Depends(permissions_required("users:update"))])
async def unlock_user(user_id: str, db: AsyncSession = Depends(db_session_dependency)):
    service = UsersService(db)
    return await service.unlock_user(user_id)


@router.post("/{user_id}/avatar", dependencies=[Depends(get_current_user), Depends(permissions_required("users:update"))])
async def upload_avatar(
    user_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(db_session_dependency),
):
    upload_dir = Path("uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = os.path.splitext(file.filename or "")[1]
    random_name = f"{uuid4().hex}{extension}"
    target = upload_dir / random_name

    with target.open("wb") as output:
        output.write(await file.read())

    service = UsersService(db)
    return await service.update_avatar(user_id, f"/uploads/avatars/{random_name}")
