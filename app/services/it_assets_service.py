from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.it_asset import ITAsset
from app.schemas.it_asset import CreateITAssetDto, UpdateITAssetDto


class ITAssetsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _parse_datetime(self, value: str | datetime | None) -> datetime:
        if isinstance(value, datetime):
            return value
        if not value:
            return datetime.now()
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return datetime.now()

    async def create(self, payload: CreateITAssetDto) -> dict:
        data = payload.model_dump()
        asset = ITAsset(
            id=str(uuid4()),
            code=data["code"],
            name=data["name"],
            category=data["category"],
            stock=data.get("stock", 0),
            min_stock=data.get("minStock", 2),
            location=data.get("location"),
            description=data.get("description"),
            image=data.get("image"),
            price=data.get("price", 0),
            received_date=self._parse_datetime(data.get("receivedDate")),
            receiver=data.get("receiver"),
            serial_number=data.get("serialNumber"),
            barcode=data.get("barcode"),
        )
        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return self._serialize(asset)

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(ITAsset).order_by(desc(ITAsset.created_at)))
        return [self._serialize(item) for item in result.scalars().all()]

    async def find_one(self, asset_id: str) -> dict:
        asset = await self.db.get(ITAsset, asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IT Asset not found")
        return self._serialize(asset)

    async def update(self, asset_id: str, payload: UpdateITAssetDto) -> dict:
        asset = await self.db.get(ITAsset, asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IT Asset not found")

        data = payload.model_dump(exclude_unset=True)
        mapping = {
            "minStock": "min_stock",
            "receivedDate": "received_date",
            "serialNumber": "serial_number",
        }
        for key, value in data.items():
            target = mapping.get(key, key)
            if target == "received_date" and value:
                value = self._parse_datetime(value)
            if hasattr(asset, target):
                setattr(asset, target, value)

        await self.db.commit()
        await self.db.refresh(asset)
        return self._serialize(asset)

    async def remove(self, asset_id: str) -> dict:
        asset = await self.db.get(ITAsset, asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IT Asset not found")
        data = {"id": asset.id, "code": asset.code, "name": asset.name}
        await self.db.delete(asset)
        await self.db.commit()
        return data

    async def update_image(self, asset_id: str, image_path: str) -> dict:
        asset = await self.db.get(ITAsset, asset_id)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IT Asset not found")
        asset.image = image_path
        await self.db.commit()
        await self.db.refresh(asset)
        return self._serialize(asset)

    def _serialize(self, asset: ITAsset) -> dict:
        return {
            "id": asset.id,
            "code": asset.code,
            "name": asset.name,
            "category": asset.category,
            "stock": asset.stock,
            "minStock": asset.min_stock,
            "location": asset.location,
            "description": asset.description,
            "image": asset.image,
            "price": asset.price,
            "receivedDate": asset.received_date,
            "receiver": asset.receiver,
            "serialNumber": asset.serial_number,
            "barcode": asset.barcode,
            "createdAt": asset.created_at,
            "updatedAt": asset.updated_at,
        }
