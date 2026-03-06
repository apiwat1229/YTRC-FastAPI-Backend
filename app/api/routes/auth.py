from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.auth import (
    ChangePasswordDto,
    LoginDto,
    RefreshTokenDto,
    RegisterDto,
    SignupDto,
)
from app.services.auth_service import AuthService
from app.services.notifications_service import NotificationsService
from app.services.refresh_tokens_service import RefreshTokensService
from app.services.users_service import UsersService

router = APIRouter(prefix="/auth", tags=["Auth"])
limiter = Limiter(key_func=get_remote_address)


def _auth_service(db: AsyncSession) -> AuthService:
    return AuthService(
        UsersService(db),
        NotificationsService(db),
        RefreshTokensService(db),
    )


@router.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    payload: LoginDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await _auth_service(db).login(payload)


@router.post("/register")
async def register(
    payload: RegisterDto, db: AsyncSession = Depends(db_session_dependency)
):
    return await _auth_service(db).register(payload)


@router.post("/signup", status_code=201)
async def signup(payload: SignupDto, db: AsyncSession = Depends(db_session_dependency)):
    return await _auth_service(db).signup(payload)


@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    payload: RefreshTokenDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await _auth_service(db).refresh(payload.refreshToken)


@router.post("/logout")
async def logout(
    payload: RefreshTokenDto,
    db: AsyncSession = Depends(db_session_dependency),
):
    return await _auth_service(db).logout(payload.refreshToken)


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    users_service = UsersService(db)
    user = await users_service.find_one(current_user["userId"])
    permissions = (
        (user.get("roleRecord") or {}).get("permissions")
        or user.get("permissions")
        or []
    )
    return {**user, "permissions": permissions}


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    return await _auth_service(db).change_password(
        current_user["userId"], payload.oldPassword, payload.newPassword
    )
