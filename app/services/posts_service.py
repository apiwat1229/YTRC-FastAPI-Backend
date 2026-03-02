from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.models.user import User
from app.schemas.post import CreatePostDto, UpdatePostDto


class PostsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: CreatePostDto, author_id: str) -> dict[str, Any]:
        post = Post(
            id=str(uuid4()),
            title=payload.title,
            content=payload.content,
            published=payload.published or False,
            author_id=author_id,
        )
        self.db.add(post)
        await self.db.commit()
        return await self.find_one(post.id)

    async def find_all(self, published: bool | None) -> list[dict[str, Any]]:
        query = select(Post).order_by(desc(Post.created_at))
        if published is not None:
            query = query.where(Post.published == published)

        result = await self.db.execute(query)
        posts = result.scalars().all()
        return [await self._serialize_post(row) for row in posts]

    async def find_one(self, post_id: str) -> dict[str, Any]:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")
        return await self._serialize_post(post)

    async def update(self, post_id: str, payload: UpdatePostDto, user_id: str, user_role: str) -> dict[str, Any]:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")

        if post.author_id != user_id and user_role != "ADMIN":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own posts")

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(post, key, value)

        await self.db.commit()
        return await self.find_one(post_id)

    async def remove(self, post_id: str, user_id: str, user_role: str) -> dict[str, Any]:
        post = await self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with ID {post_id} not found")

        if post.author_id != user_id and user_role != "ADMIN":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own posts")

        data = await self._serialize_post(post)
        await self.db.delete(post)
        await self.db.commit()
        return data

    async def _serialize_post(self, post: Post) -> dict[str, Any]:
        author = await self.db.get(User, post.author_id)
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "published": post.published,
            "authorId": post.author_id,
            "createdAt": post.created_at,
            "updatedAt": post.updated_at,
            "author": {
                "id": author.id,
                "email": author.email,
                "role": author.role,
            }
            if author
            else None,
        }
