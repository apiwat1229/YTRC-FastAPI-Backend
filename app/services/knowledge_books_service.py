import os
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book_view import BookView
from app.models.knowledge_book import KnowledgeBook
from app.models.user import User
from app.schemas.knowledge_book import CreateKnowledgeBookDto, UpdateKnowledgeBookDto


class KnowledgeBooksService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _parse_datetime(self, value: str | datetime | None) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None

    async def create(self, payload: CreateKnowledgeBookDto) -> dict:
        data = payload.model_dump()
        book = KnowledgeBook(
            id=str(uuid4()),
            title=data["title"],
            description=data.get("description"),
            category=data["category"],
            file_type=data["fileType"],
            file_name=data["fileName"],
            file_path=data["filePath"],
            file_size=data["fileSize"],
            cover_image=data.get("coverImage"),
            author=data.get("author"),
            tags=data.get("tags", []),
            uploaded_by=data["uploadedBy"],
            training_date=self._parse_datetime(data.get("trainingDate")),
            attendees=data.get("attendees", 0),
        )
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return await self.find_one(book.id)

    async def find_all(self, filters: dict | None = None) -> list[dict]:
        filters = filters or {}
        query = select(KnowledgeBook)

        conditions = []
        if filters.get("category"):
            conditions.append(KnowledgeBook.category == filters["category"])
        if filters.get("uploadedBy"):
            conditions.append(KnowledgeBook.uploaded_by == filters["uploadedBy"])
        if filters.get("isPublished") is not None:
            conditions.append(KnowledgeBook.is_published == filters["isPublished"])
        if filters.get("search"):
            search_term = f"%{filters['search']}%"
            conditions.append(
                or_(
                    KnowledgeBook.title.ilike(search_term),
                    KnowledgeBook.description.ilike(search_term),
                    KnowledgeBook.author.ilike(search_term),
                )
            )
        if filters.get("tags"):
            for tag in filters["tags"]:
                conditions.append(KnowledgeBook.tags.contains([tag]))

        if conditions:
            query = query.where(*conditions)

        query = query.order_by(desc(KnowledgeBook.created_at))
        result = await self.db.execute(query)
        books = result.scalars().all()

        output = []
        for book in books:
            uploader = await self.db.get(User, book.uploaded_by)
            view_count = await self.db.scalar(select(func.count()).select_from(BookView).where(BookView.book_id == book.id))
            output.append(
                {
                    "id": book.id,
                    "title": book.title,
                    "description": book.description,
                    "category": book.category,
                    "fileType": book.file_type,
                    "fileName": book.file_name,
                    "filePath": book.file_path,
                    "fileSize": book.file_size,
                    "coverImage": book.cover_image,
                    "author": book.author,
                    "uploadedBy": book.uploaded_by,
                    "views": book.views,
                    "downloads": book.downloads,
                    "tags": book.tags,
                    "isPublished": book.is_published,
                    "trainingDate": book.training_date,
                    "attendees": book.attendees,
                    "createdAt": book.created_at,
                    "updatedAt": book.updated_at,
                    "uploader": {
                        "id": uploader.id,
                        "displayName": uploader.display_name,
                        "firstName": uploader.first_name,
                        "lastName": uploader.last_name,
                    }
                    if uploader
                    else None,
                    "_count": {"viewHistory": view_count or 0},
                }
            )
        return output

    async def find_one(self, book_id: str) -> dict:
        book = await self.db.get(KnowledgeBook, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        uploader = await self.db.get(User, book.uploaded_by)
        view_count = await self.db.scalar(select(func.count()).select_from(BookView).where(BookView.book_id == book_id))

        return {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "category": book.category,
            "fileType": book.file_type,
            "fileName": book.file_name,
            "filePath": book.file_path,
            "fileSize": book.file_size,
            "coverImage": book.cover_image,
            "author": book.author,
            "uploadedBy": book.uploaded_by,
            "views": book.views,
            "downloads": book.downloads,
            "tags": book.tags,
            "isPublished": book.is_published,
            "trainingDate": book.training_date,
            "attendees": book.attendees,
            "createdAt": book.created_at,
            "updatedAt": book.updated_at,
            "uploader": {
                "id": uploader.id,
                "displayName": uploader.display_name,
                "firstName": uploader.first_name,
                "lastName": uploader.last_name,
            }
            if uploader
            else None,
            "_count": {"viewHistory": view_count or 0},
        }

    async def update(self, book_id: str, payload: UpdateKnowledgeBookDto) -> dict:
        book = await self.db.get(KnowledgeBook, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        data = payload.model_dump(exclude_unset=True)
        mapping = {"isPublished": "is_published", "trainingDate": "training_date"}

        for key, value in data.items():
            target = mapping.get(key, key)
            if target == "training_date" and value:
                value = self._parse_datetime(value)
            if hasattr(book, target):
                setattr(book, target, value)

        await self.db.commit()
        return await self.find_one(book_id)

    async def remove(self, book_id: str) -> dict:
        book = await self.db.get(KnowledgeBook, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        try:
            if book.file_path and os.path.exists(book.file_path):
                os.remove(book.file_path)
        except Exception:
            pass

        try:
            if book.cover_image and os.path.exists(book.cover_image):
                os.remove(book.cover_image)
        except Exception:
            pass

        data = {"id": book.id, "title": book.title}
        await self.db.delete(book)
        await self.db.commit()
        return data

    async def track_view(self, book_id: str, user_id: str) -> None:
        book = await self.db.get(KnowledgeBook, book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        view = BookView(id=str(uuid4()), book_id=book_id, user_id=user_id)
        self.db.add(view)

        book.views += 1
        await self.db.commit()

    async def increment_download(self, book_id: str) -> None:
        book = await self.db.get(KnowledgeBook, book_id)
        if book:
            book.downloads += 1
            await self.db.commit()

    async def get_categories(self) -> list[str]:
        result = await self.db.execute(
            select(KnowledgeBook.category).where(KnowledgeBook.is_published == True).distinct()
        )
        return [row[0] for row in result.all()]

    async def get_stats(self) -> dict:
        total = await self.db.scalar(select(func.count()).select_from(KnowledgeBook).where(KnowledgeBook.is_published == True))

        by_category_result = await self.db.execute(
            select(KnowledgeBook.category, func.count())
            .where(KnowledgeBook.is_published == True)
            .group_by(KnowledgeBook.category)
        )
        by_category = [{"category": row[0], "_count": row[1]} for row in by_category_result.all()]

        top_viewed_result = await self.db.execute(
            select(KnowledgeBook)
            .where(KnowledgeBook.is_published == True)
            .order_by(desc(KnowledgeBook.views))
            .limit(10)
        )
        top_viewed = [
            {
                "id": book.id,
                "title": book.title,
                "views": book.views,
                "downloads": book.downloads,
            }
            for book in top_viewed_result.scalars().all()
        ]

        return {"total": total or 0, "byCategory": by_category, "topViewed": top_viewed}
