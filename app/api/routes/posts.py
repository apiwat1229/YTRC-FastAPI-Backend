from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import db_session_dependency, get_current_user
from app.schemas.post import CreatePostDto, UpdatePostDto
from app.services.posts_service import PostsService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", dependencies=[Depends(get_current_user)])
async def create_post(
    payload: CreatePostDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    service = PostsService(db)
    return await service.create(payload, current_user["userId"])


@router.get("")
async def find_all_posts(
    published: str | None = Query(default=None),
    db: AsyncSession = Depends(db_session_dependency),
):
    parsed = True if published == "true" else False if published == "false" else None
    service = PostsService(db)
    return await service.find_all(parsed)


@router.get("/{post_id}")
async def find_post(post_id: str, db: AsyncSession = Depends(db_session_dependency)):
    service = PostsService(db)
    return await service.find_one(post_id)


@router.patch("/{post_id}", dependencies=[Depends(get_current_user)])
async def update_post(
    post_id: str,
    payload: UpdatePostDto,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    service = PostsService(db)
    return await service.update(post_id, payload, current_user["userId"], current_user.get("role") or "")


@router.delete("/{post_id}", dependencies=[Depends(get_current_user)])
async def delete_post(
    post_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(db_session_dependency),
):
    service = PostsService(db)
    return await service.remove(post_id, current_user["userId"], current_user.get("role") or "")
