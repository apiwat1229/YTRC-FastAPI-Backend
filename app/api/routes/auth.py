from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.auth import (ChangePasswordDto, LoginDto, RegisterDto,
                              SignupDto)
from app.services.auth_service import AuthService
from app.services.notifications_service import NotificationsService
from app.services.users_service import UsersService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(payload: LoginDto, db: AsyncSession = Depends(db_session_dependency)):
    auth_service = AuthService(UsersService(db), NotificationsService(db))
    return await auth_service.login(payload)


@router.post("/register")
async def register(payload: RegisterDto, db: AsyncSession = Depends(db_session_dependency)):
    auth_service = AuthService(UsersService(db), NotificationsService(db))
    return await auth_service.register(payload)


@router.post("/signup", status_code=201)
async def signup(payload: SignupDto, db: AsyncSession = Depends(db_session_dependency)):
    auth_service = AuthService(UsersService(db), NotificationsService(db))
    return await auth_service.signup(payload)


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    users_service = UsersService(db)
    user = await users_service.find_one(current_user["userId"])
    permissions = (user.get("roleRecord") or {}).get("permissions") or user.get("permissions") or []
    return {**user, "permissions": permissions}


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    auth_service = AuthService(UsersService(db), NotificationsService(db))
    return await auth_service.change_password(current_user["userId"], payload.oldPassword, payload.newPassword)
