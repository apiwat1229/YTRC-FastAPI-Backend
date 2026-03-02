from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pool import Pool
from app.models.pool_item import PoolItem


class PoolsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_pools(self) -> list[dict]:
        result = await self.db.execute(select(Pool).order_by(asc(Pool.name)))
        pools = result.scalars().all()
        output = []
        for pool in pools:
            count_result = await self.db.execute(select(PoolItem).where(PoolItem.pool_id == pool.id))
            items = count_result.scalars().all()
            data = self._serialize_pool(pool)
            data["_count"] = {"items": len(items)}
            output.append(data)
        return output

    async def get_pool(self, pool_id: str) -> dict:
        pool = await self.db.get(Pool, pool_id)
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")
        items_result = await self.db.execute(select(PoolItem).where(PoolItem.pool_id == pool_id))
        data = self._serialize_pool(pool)
        data["items"] = [self._serialize_item(item) for item in items_result.scalars().all()]
        return data

    async def create_pool(self, data: dict) -> dict:
        pool = Pool(
            id=str(uuid4()),
            name=data.get("name") or f"Pool {int(datetime.now().timestamp())}",
            status=data.get("status") or "empty",
            grade=data.get("grade") or "-",
            rubber_type=data.get("rubberType") or "-",
            capacity=float(data.get("capacity") or 3000),
            total_weight=float(data.get("totalWeight") or 0),
            total_gross_weight=float(data.get("totalGrossWeight") or 0),
        )
        self.db.add(pool)
        await self.db.commit()
        await self.db.refresh(pool)
        return self._serialize_pool(pool)

    async def update_pool(self, pool_id: str, data: dict) -> dict:
        pool = await self.db.get(Pool, pool_id)
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

        mapping = {
            "rubberType": "rubber_type",
            "totalWeight": "total_weight",
            "totalGrossWeight": "total_gross_weight",
            "closeDate": "close_date",
            "fillingDate": "filling_date",
        }
        for key, value in data.items():
            target = mapping.get(key, key)
            if hasattr(pool, target):
                setattr(pool, target, value)

        await self.db.commit()
        await self.db.refresh(pool)
        return self._serialize_pool(pool)

    async def add_items(self, pool_id: str, items: list[dict]) -> dict:
        pool = await self.db.get(Pool, pool_id)
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")
        if pool.status == "closed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add items to a closed pool")

        total_net = 0.0
        total_gross = 0.0
        for item in items:
            net = float(item.get("net_weight") or item.get("displayWeight") or 0)
            gross = float(item.get("gross_weight") or item.get("weightIn") or 0)
            total_net += net
            total_gross += gross

            row = PoolItem(
                id=str(uuid4()),
                pool_id=pool_id,
                booking_id=item.get("booking_id") or item.get("id") or "-",
                lot_number=item.get("lot_number") or item.get("lotNo") or "-",
                supplier_name=item.get("supplier_name") or item.get("supplierName") or "-",
                supplier_code=item.get("supplier_code") or item.get("supplierCode") or "-",
                date=datetime.fromisoformat(str(item.get("date")).replace("Z", "+00:00"))
                if item.get("date")
                else datetime.now(timezone.utc),
                net_weight=net,
                gross_weight=gross,
                grade=item.get("grade") or "-",
                rubber_type=item.get("rubber_type") or item.get("displayRubberType") or "-",
            )
            self.db.add(row)

        pool.total_weight = float(pool.total_weight or 0) + total_net
        pool.total_gross_weight = float(pool.total_gross_weight or 0) + total_gross

        if pool.status == "empty" and items:
            first = items[0]
            pool.status = "open"
            pool.filling_date = datetime.now(timezone.utc)
            pool.grade = first.get("grade") or "-"
            pool.rubber_type = first.get("rubber_type") or first.get("displayRubberType") or "-"

        await self.db.commit()
        return await self.get_pool(pool_id)

    async def remove_item(self, pool_id: str, booking_id: str) -> dict:
        result = await self.db.execute(
            select(PoolItem)
            .where(PoolItem.pool_id == pool_id, PoolItem.booking_id == booking_id)
            .limit(1)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in this pool")

        pool = await self.db.get(Pool, pool_id)
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")

        await self.db.delete(item)
        await self.db.flush()

        pool.total_weight = max(0.0, float(pool.total_weight or 0) - float(item.net_weight or 0))
        pool.total_gross_weight = max(0.0, float(pool.total_gross_weight or 0) - float(item.gross_weight or 0))

        count_result = await self.db.execute(select(PoolItem).where(PoolItem.pool_id == pool_id))
        remaining = count_result.scalars().all()
        if len(remaining) == 0:
            pool.status = "empty"
            pool.grade = "-"
            pool.rubber_type = "-"
            pool.filling_date = None
            pool.total_weight = 0
            pool.total_gross_weight = 0

        await self.db.commit()
        return self._serialize_pool(pool)

    async def close_pool(self, pool_id: str, close_date: datetime | None) -> dict:
        pool = await self.db.get(Pool, pool_id)
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")
        pool.status = "closed"
        pool.close_date = close_date or datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(pool)
        return self._serialize_pool(pool)

    async def reopen_pool(self, pool_id: str) -> dict:
        pool = await self.db.get(Pool, pool_id)
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool not found")
        pool.status = "open"
        pool.close_date = None
        await self.db.commit()
        await self.db.refresh(pool)
        return self._serialize_pool(pool)

    async def seed_pools(self) -> dict:
        count_result = await self.db.execute(select(Pool))
        existing = count_result.scalars().all()
        if existing:
            return {"message": "Already seeded", "count": len(existing)}

        for index in range(24):
            self.db.add(
                Pool(
                    id=str(uuid4()),
                    name=f"Pool {index + 1}",
                    status="empty",
                    capacity=3000,
                    grade="-",
                    rubber_type="-",
                    total_weight=0,
                    total_gross_weight=0,
                )
            )
        await self.db.commit()
        return {"message": "Seeded 24 pools", "count": 24}

    def _serialize_pool(self, pool: Pool) -> dict:
        return {
            "id": pool.id,
            "name": pool.name,
            "status": pool.status,
            "grade": pool.grade,
            "rubberType": pool.rubber_type,
            "capacity": pool.capacity,
            "totalWeight": pool.total_weight,
            "totalGrossWeight": pool.total_gross_weight,
            "openDate": pool.open_date,
            "closeDate": pool.close_date,
            "emptyDate": pool.empty_date,
            "fillingDate": pool.filling_date,
            "productionPlan": pool.production_plan,
            "createdAt": pool.created_at,
            "updatedAt": pool.updated_at,
        }

    def _serialize_item(self, item: PoolItem) -> dict:
        return {
            "id": item.id,
            "poolId": item.pool_id,
            "bookingId": item.booking_id,
            "lotNumber": item.lot_number,
            "supplierName": item.supplier_name,
            "supplierCode": item.supplier_code,
            "date": item.date,
            "netWeight": item.net_weight,
            "grossWeight": item.gross_weight,
            "grade": item.grade,
            "rubberType": item.rubber_type,
            "createdAt": item.created_at,
        }
