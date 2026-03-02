from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.production_report_row import ProductionReportRow
from app.models.shipping_plan import ShippingPlan
from app.models.shipping_plan_item import ShippingPlanItem
from app.schemas.shipping_plan import CreateShippingPlanDto


class ShippingPlansService:
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

    async def create(self, payload: CreateShippingPlanDto) -> dict:
        data = payload.model_dump()
        try:
            plan = ShippingPlan(
                id=str(uuid4()),
                plan_no=data["planNo"],
                customer=data.get("customer"),
                plan_date=self._parse_datetime(data["planDate"]),
                status="DRAFT",
                remark=data.get("remark"),
            )
            self.db.add(plan)
            await self.db.flush()

            for item_data in data.get("items", []):
                item = ShippingPlanItem(
                    id=str(uuid4()),
                    shipping_plan_id=plan.id,
                    row_id=item_data["rowId"],
                    pallet_no=item_data["palletNo"],
                )
                self.db.add(item)

            await self.db.commit()
            return await self.find_one(plan.id)
        except Exception as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create shipping plan: {str(exc)}",
            ) from exc

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(ShippingPlan).order_by(desc(ShippingPlan.created_at)))
        plans = result.scalars().all()
        return [await self.find_one(plan.id) for plan in plans]

    async def find_one(self, plan_id: str) -> dict:
        plan = await self.db.get(ShippingPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipping plan not found")

        items_result = await self.db.execute(select(ShippingPlanItem).where(ShippingPlanItem.shipping_plan_id == plan_id))
        items = items_result.scalars().all()

        serialized_items = []
        for item in items:
            row = await self.db.get(ProductionReportRow, item.row_id)
            serialized_items.append(
                {
                    "id": item.id,
                    "shippingPlanId": item.shipping_plan_id,
                    "rowId": item.row_id,
                    "palletNo": item.pallet_no,
                    "createdAt": item.created_at,
                    "row": {
                        "id": row.id,
                        "reportId": row.report_id,
                        "startTime": row.start_time,
                        "palletType": row.pallet_type,
                        "lotNo": row.lot_no,
                        "weight1": row.weight_1,
                        "weight2": row.weight_2,
                        "weight3": row.weight_3,
                        "weight4": row.weight_4,
                        "weight5": row.weight_5,
                    }
                    if row
                    else None,
                }
            )

        return {
            "id": plan.id,
            "planNo": plan.plan_no,
            "customer": plan.customer,
            "planDate": plan.plan_date,
            "status": plan.status,
            "remark": plan.remark,
            "createdAt": plan.created_at,
            "updatedAt": plan.updated_at,
            "items": serialized_items,
        }

    async def find_available_pallets(self) -> list[dict]:
        rows_result = await self.db.execute(
            select(ProductionReportRow).where(
                or_(
                    ProductionReportRow.weight_1_status == "PASS",
                    ProductionReportRow.weight_2_status == "PASS",
                    ProductionReportRow.weight_3_status == "PASS",
                    ProductionReportRow.weight_4_status == "PASS",
                    ProductionReportRow.weight_5_status == "PASS",
                )
            )
        )
        rows = rows_result.scalars().all()

        available = []
        for row in rows:
            shipped_result = await self.db.execute(
                select(ShippingPlanItem).where(ShippingPlanItem.row_id == row.id)
            )
            shipped_items = shipped_result.scalars().all()
            shipped_pallets = {item.pallet_no for item in shipped_items}

            for i in range(1, 6):
                weight = getattr(row, f"weight_{i}")
                status = getattr(row, f"weight_{i}_status")
                if status == "PASS" and weight and weight > 0 and i not in shipped_pallets:
                    available.append(
                        {
                            "rowId": row.id,
                            "lotNo": row.lot_no,
                            "palletNo": i,
                            "weight": weight,
                            "startTime": row.start_time,
                            "palletType": row.pallet_type,
                        }
                    )

        return available
