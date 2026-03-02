from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.production_report import ProductionReport
from app.models.production_report_row import ProductionReportRow
from app.schemas.production_report import CreateProductionReportDto


class ProductionReportsService:
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

    async def create(self, payload: CreateProductionReportDto) -> dict:
        data = payload.model_dump()
        try:
            report = ProductionReport(
                id=str(uuid4()),
                dryer_name=data["dryerName"],
                book_no=data["bookNo"],
                page_no=data["pageNo"],
                production_date=self._parse_datetime(data["productionDate"]),
                shift=data["shift"],
                grade=data["grade"],
                ratio_cl=data.get("ratioCL"),
                ratio_uss=data.get("ratioUSS"),
                ratio_cutting=data.get("ratioCutting"),
                weight_pallet_remained=data.get("weightPalletRemained"),
                sample_accum_1=data.get("sampleAccum1"),
                sample_accum_2=data.get("sampleAccum2"),
                sample_accum_3=data.get("sampleAccum3"),
                sample_accum_4=data.get("sampleAccum4"),
                sample_accum_5=data.get("sampleAccum5"),
                bale_bag_lot_no=data.get("baleBagLotNo"),
                checked_by=data.get("checkedBy"),
                judged_by=data.get("judgedBy"),
                issued_by=data.get("issuedBy"),
                issued_at=self._parse_datetime(data.get("issuedAt")) if data.get("issuedAt") else None,
                status=data.get("status") or "DRAFT",
            )
            self.db.add(report)
            await self.db.flush()

            for row_data in data.get("rows", []):
                row = ProductionReportRow(
                    id=str(uuid4()),
                    report_id=report.id,
                    start_time=row_data["startTime"],
                    pallet_type=row_data["palletType"],
                    lot_no=row_data["lotNo"],
                    weight_1=row_data.get("weight1"),
                    weight_2=row_data.get("weight2"),
                    weight_3=row_data.get("weight3"),
                    weight_4=row_data.get("weight4"),
                    weight_5=row_data.get("weight5"),
                    sample_count=row_data.get("sampleCount"),
                    weight_1_status=row_data.get("weight1Status"),
                    weight_2_status=row_data.get("weight2Status"),
                    weight_3_status=row_data.get("weight3Status"),
                    weight_4_status=row_data.get("weight4Status"),
                    weight_5_status=row_data.get("weight5Status"),
                    sample_status=row_data.get("sampleStatus"),
                )
                self.db.add(row)

            await self.db.commit()
            return await self.find_one(report.id)
        except Exception as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create report: {str(exc)}",
            ) from exc

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(ProductionReport).order_by(desc(ProductionReport.created_at)))
        reports = result.scalars().all()
        return [await self.find_one(report.id) for report in reports]

    async def find_one(self, report_id: str) -> dict:
        report = await self.db.get(ProductionReport, report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        rows_result = await self.db.execute(
            select(ProductionReportRow).where(ProductionReportRow.report_id == report_id)
        )
        rows = rows_result.scalars().all()

        return {
            "id": report.id,
            "dryerName": report.dryer_name,
            "bookNo": report.book_no,
            "pageNo": report.page_no,
            "productionDate": report.production_date,
            "shift": report.shift,
            "grade": report.grade,
            "ratioCL": report.ratio_cl,
            "ratioUSS": report.ratio_uss,
            "ratioCutting": report.ratio_cutting,
            "weightPalletRemained": report.weight_pallet_remained,
            "sampleAccum1": report.sample_accum_1,
            "sampleAccum2": report.sample_accum_2,
            "sampleAccum3": report.sample_accum_3,
            "sampleAccum4": report.sample_accum_4,
            "sampleAccum5": report.sample_accum_5,
            "baleBagLotNo": report.bale_bag_lot_no,
            "checkedBy": report.checked_by,
            "judgedBy": report.judged_by,
            "issuedBy": report.issued_by,
            "issuedAt": report.issued_at,
            "status": report.status,
            "createdAt": report.created_at,
            "updatedAt": report.updated_at,
            "rows": [
                {
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
                    "sampleCount": row.sample_count,
                    "weight1Status": row.weight_1_status,
                    "weight2Status": row.weight_2_status,
                    "weight3Status": row.weight_3_status,
                    "weight4Status": row.weight_4_status,
                    "weight5Status": row.weight_5_status,
                    "sampleStatus": row.sample_status,
                }
                for row in rows
            ],
        }

    async def update(self, report_id: str, payload: CreateProductionReportDto) -> dict:
        report = await self.db.get(ProductionReport, report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

        data = payload.model_dump()
        try:
            old_rows = await self.db.execute(
                select(ProductionReportRow).where(ProductionReportRow.report_id == report_id)
            )
            for row in old_rows.scalars().all():
                await self.db.delete(row)

            report.dryer_name = data["dryerName"]
            report.book_no = data["bookNo"]
            report.page_no = data["pageNo"]
            report.production_date = self._parse_datetime(data["productionDate"])
            report.shift = data["shift"]
            report.grade = data["grade"]
            report.ratio_cl = data.get("ratioCL")
            report.ratio_uss = data.get("ratioUSS")
            report.ratio_cutting = data.get("ratioCutting")
            report.weight_pallet_remained = data.get("weightPalletRemained")
            report.sample_accum_1 = data.get("sampleAccum1")
            report.sample_accum_2 = data.get("sampleAccum2")
            report.sample_accum_3 = data.get("sampleAccum3")
            report.sample_accum_4 = data.get("sampleAccum4")
            report.sample_accum_5 = data.get("sampleAccum5")
            report.bale_bag_lot_no = data.get("baleBagLotNo")
            report.checked_by = data.get("checkedBy")
            report.judged_by = data.get("judgedBy")
            report.issued_by = data.get("issuedBy")
            report.issued_at = self._parse_datetime(data.get("issuedAt")) if data.get("issuedAt") else None

            for row_data in data.get("rows", []):
                row = ProductionReportRow(
                    id=str(uuid4()),
                    report_id=report.id,
                    start_time=row_data["startTime"],
                    pallet_type=row_data["palletType"],
                    lot_no=row_data["lotNo"],
                    weight_1=row_data.get("weight1"),
                    weight_2=row_data.get("weight2"),
                    weight_3=row_data.get("weight3"),
                    weight_4=row_data.get("weight4"),
                    weight_5=row_data.get("weight5"),
                    sample_count=row_data.get("sampleCount"),
                    weight_1_status=row_data.get("weight1Status"),
                    weight_2_status=row_data.get("weight2Status"),
                    weight_3_status=row_data.get("weight3Status"),
                    weight_4_status=row_data.get("weight4Status"),
                    weight_5_status=row_data.get("weight5Status"),
                    sample_status=row_data.get("sampleStatus"),
                )
                self.db.add(row)

            await self.db.commit()
            return await self.find_one(report_id)
        except Exception as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update report: {str(exc)}",
            ) from exc

    async def remove(self, report_id: str) -> dict:
        report = await self.db.get(ProductionReport, report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        data = {"id": report.id, "dryerName": report.dryer_name, "bookNo": report.book_no}
        await self.db.delete(report)
        await self.db.commit()
        return data
