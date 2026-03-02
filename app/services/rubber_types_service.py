from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rubber_type import RubberType
from app.schemas.rubber_type import CreateRubberTypeDto, UpdateRubberTypeDto


class RubberTypesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, payload: CreateRubberTypeDto) -> dict:
        model = RubberType(
            id=str(uuid4()),
            code=payload.code,
            name=payload.name,
            category=payload.category,
            description=payload.description,
            is_active=(payload.status == "ACTIVE") if payload.status is not None else bool(payload.is_active),
        )
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._serialize(model)

    async def find_all(self, include_deleted: bool = False) -> list[dict]:
        query = select(RubberType).order_by(asc(RubberType.code))
        if not include_deleted:
            query = query.where(RubberType.deleted_at.is_(None))
        result = await self.db.execute(query)
        return [self._serialize(item) for item in result.scalars().all()]

    async def find_one(self, rubber_type_id: str) -> dict:
        item = await self.db.get(RubberType, rubber_type_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubber type not found")
        return self._serialize(item)

    async def update(self, rubber_type_id: str, payload: UpdateRubberTypeDto) -> dict:
        item = await self.db.get(RubberType, rubber_type_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubber type not found")

        data = payload.model_dump(exclude_unset=True)
        if "status" in data:
            item.is_active = data["status"] == "ACTIVE"
            data.pop("status")
        if "is_active" in data:
            item.is_active = bool(data.pop("is_active"))

        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)

        await self.db.commit()
        await self.db.refresh(item)
        return self._serialize(item)

    async def remove(self, rubber_type_id: str) -> dict:
        item = await self.db.get(RubberType, rubber_type_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubber type not found")

        data = self._serialize(item)
        await self.db.delete(item)
        await self.db.commit()
        return data

    async def soft_delete(self, rubber_type_id: str, user_id: str) -> dict:
        item = await self.db.get(RubberType, rubber_type_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubber type not found")

        item.deleted_at = datetime.utcnow()
        item.deleted_by = user_id
        await self.db.commit()
        await self.db.refresh(item)
        return self._serialize(item)

    async def restore(self, rubber_type_id: str) -> dict:
        item = await self.db.get(RubberType, rubber_type_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubber type not found")

        item.deleted_at = None
        item.deleted_by = None
        await self.db.commit()
        await self.db.refresh(item)
        return self._serialize(item)

    def _serialize(self, item: RubberType) -> dict:
        return {
            "id": item.id,
            "code": item.code,
            "name": item.name,
            "category": item.category,
            "description": item.description,
            "is_active": item.is_active,
            "status": "ACTIVE" if item.is_active else "INACTIVE",
            "deletedAt": item.deleted_at,
            "deletedBy": item.deleted_by,
            "createdAt": item.created_at,
            "updatedAt": item.updated_at,
        }
