from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user, permissions_required
from app.core.permissions import ROLES_CREATE, ROLES_DELETE, ROLES_READ, ROLES_UPDATE
from app.schemas.role import CreateRoleDto, UpdateRoleDto
from app.services.roles_service import RolesService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", dependencies=[Depends(get_current_user), Depends(permissions_required(ROLES_READ))])
async def find_all_roles(db: AsyncSession = Depends(db_session_dependency)):
    return await RolesService(db).find_all()


@router.get("/{role_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(ROLES_READ))])
async def find_one_role(role_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await RolesService(db).find_one(role_id)


@router.post("", dependencies=[Depends(get_current_user), Depends(permissions_required(ROLES_CREATE))])
async def create_role(payload: CreateRoleDto, db: AsyncSession = Depends(db_session_dependency)):
    return await RolesService(db).create(payload)


@router.patch("/{role_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(ROLES_UPDATE))])
async def update_role(role_id: str, payload: UpdateRoleDto, db: AsyncSession = Depends(db_session_dependency)):
    return await RolesService(db).update(role_id, payload)


@router.delete("/{role_id}", dependencies=[Depends(get_current_user), Depends(permissions_required(ROLES_DELETE))])
async def delete_role(role_id: str, db: AsyncSession = Depends(db_session_dependency)):
    return await RolesService(db).remove(role_id)
