from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_order import JobOrder
from app.models.job_order_log import JobOrderLog
from app.schemas.job_order import CreateJobOrderDto, UpdateJobOrderDto


class JobOrdersService:
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

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(JobOrder).order_by(desc(JobOrder.created_at)))
        orders = result.scalars().all()
        return [await self.find_one(order.id) for order in orders]

    async def find_one(self, order_id: str) -> dict:
        order = await self.db.get(JobOrder, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Order not found")

        logs_result = await self.db.execute(
            select(JobOrderLog).where(JobOrderLog.job_order_id == order_id).order_by(JobOrderLog.date)
        )
        logs = logs_result.scalars().all()

        return {
            "id": order.id,
            "bookNo": order.book_no,
            "no": order.no,
            "jobOrderNo": order.job_order_no,
            "contractNo": order.contract_no,
            "grade": order.grade,
            "otherGrade": order.other_grade,
            "quantityBale": order.quantity_bale,
            "palletType": order.pallet_type,
            "orderQuantity": order.order_quantity,
            "palletMarking": order.pallet_marking,
            "note": order.note,
            "qaName": order.qa_name,
            "qaDate": order.qa_date,
            "isClosed": order.is_closed,
            "productionName": order.production_name,
            "productionDate": order.production_date,
            "createdAt": order.created_at,
            "updatedAt": order.updated_at,
            "logs": [
                {
                    "id": log.id,
                    "jobOrderId": log.job_order_id,
                    "date": log.date,
                    "shift": log.shift,
                    "lotStart": log.lot_start,
                    "lotEnd": log.lot_end,
                    "quantity": log.quantity,
                    "sign": log.sign,
                    "createdAt": log.created_at,
                    "updatedAt": log.updated_at,
                }
                for log in logs
            ],
        }

    async def create(self, payload: CreateJobOrderDto) -> dict:
        data = payload.model_dump()

        existing = await self.db.execute(select(JobOrder).where(JobOrder.job_order_no == data["jobOrderNo"]))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job Order number already exists: {data['jobOrderNo']}",
            )

        try:
            order = JobOrder(
                id=str(uuid4()),
                book_no=data.get("bookNo", ""),
                no=data.get("no", 0),
                job_order_no=data["jobOrderNo"],
                contract_no=data["contractNo"],
                grade=data["grade"],
                other_grade=data.get("otherGrade"),
                quantity_bale=data["quantityBale"],
                pallet_type=data["palletType"],
                order_quantity=data["orderQuantity"],
                pallet_marking=data.get("palletMarking", True),
                note=data.get("note"),
                qa_name=data["qaName"],
                qa_date=self._parse_datetime(data["qaDate"]),
            )
            self.db.add(order)
            await self.db.flush()

            for log_data in data.get("logs", []):
                log = JobOrderLog(
                    id=str(uuid4()),
                    job_order_id=order.id,
                    date=self._parse_datetime(log_data["date"]),
                    shift=log_data["shift"],
                    lot_start=log_data["lotStart"],
                    lot_end=log_data["lotEnd"],
                    quantity=log_data["quantity"],
                    sign=log_data.get("sign"),
                )
                self.db.add(log)

            await self.db.commit()
            return await self.find_one(order.id)
        except Exception as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create job order: {str(exc)}",
            ) from exc

    async def update(self, order_id: str, payload: UpdateJobOrderDto) -> dict:
        order = await self.db.get(JobOrder, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Order not found")

        data = payload.model_dump(exclude_unset=True)

        if "jobOrderNo" in data and data["jobOrderNo"] != order.job_order_no:
            existing = await self.db.execute(select(JobOrder).where(JobOrder.job_order_no == data["jobOrderNo"]))
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Job Order number already exists"
                )

        try:
            mapping = {
                "bookNo": "book_no",
                "jobOrderNo": "job_order_no",
                "contractNo": "contract_no",
                "otherGrade": "other_grade",
                "quantityBale": "quantity_bale",
                "palletType": "pallet_type",
                "orderQuantity": "order_quantity",
                "palletMarking": "pallet_marking",
                "qaName": "qa_name",
                "qaDate": "qa_date",
                "isClosed": "is_closed",
                "productionName": "production_name",
                "productionDate": "production_date",
            }

            for key, value in data.items():
                if key == "logs":
                    continue
                target = mapping.get(key, key)
                if target in {"qa_date", "production_date"} and value:
                    value = self._parse_datetime(value)
                if hasattr(order, target):
                    setattr(order, target, value)

            if "logs" in data:
                old_logs = await self.db.execute(select(JobOrderLog).where(JobOrderLog.job_order_id == order_id))
                for log in old_logs.scalars().all():
                    await self.db.delete(log)

                for log_data in data["logs"]:
                    log = JobOrderLog(
                        id=str(uuid4()),
                        job_order_id=order.id,
                        date=self._parse_datetime(log_data["date"]),
                        shift=log_data["shift"],
                        lot_start=log_data["lotStart"],
                        lot_end=log_data["lotEnd"],
                        quantity=log_data["quantity"],
                        sign=log_data.get("sign"),
                    )
                    self.db.add(log)

            await self.db.commit()
            return await self.find_one(order_id)
        except Exception as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update job order: {str(exc)}",
            ) from exc

    async def remove(self, order_id: str) -> dict:
        order = await self.db.get(JobOrder, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Order not found")

        logs = await self.db.execute(select(JobOrderLog).where(JobOrderLog.job_order_id == order_id))
        for log in logs.scalars().all():
            await self.db.delete(log)

        data = {"id": order.id, "jobOrderNo": order.job_order_no}
        await self.db.delete(order)
        await self.db.commit()
        return data

    async def close_job(self, order_id: str, production_info: dict) -> dict:
        order = await self.db.get(JobOrder, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job Order not found")

        order.is_closed = True
        order.production_name = production_info.get("productionName")
        order.production_date = self._parse_datetime(production_info.get("productionDate"))

        await self.db.commit()
        return await self.find_one(order_id)
