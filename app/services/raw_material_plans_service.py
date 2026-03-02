from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.raw_material_plan import RawMaterialPlan
from app.models.raw_material_plan_pool_detail import RawMaterialPlanPoolDetail
from app.models.raw_material_plan_row import RawMaterialPlanRow
from app.schemas.raw_material_plan import CreateRawMaterialPlanDto


class RawMaterialPlansService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _parse_date(self, value: datetime | str | None) -> datetime:
        if isinstance(value, datetime):
            return value
        if not value:
            return datetime.now()
        text = str(value)
        for fmt in ("%d %b %y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(text.replace("Z", ""), fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return datetime.now()

    def _clean_number(self, value):
        if value in (None, "", "-"):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    async def create(self, payload: CreateRawMaterialPlanDto) -> dict:
        data = payload.model_dump()
        try:
            plan = RawMaterialPlan(
                id=str(uuid4()),
                plan_no=data["planNo"],
                revision_no=data["revisionNo"],
                ref_production_no=data["refProductionNo"],
                issued_date=self._parse_date(data.get("issuedDate")),
                creator=data.get("issueBy") or "System",
                checker=data.get("verifiedBy"),
                status="DRAFT",
            )
            self.db.add(plan)
            await self.db.flush()

            rows = self._build_rows(plan.id, data.get("rows") or [])
            pool_details = self._build_pool_details(plan.id, data.get("poolDetails") or [])

            for row in rows:
                self.db.add(row)
            for detail in pool_details:
                self.db.add(detail)

            await self.db.commit()
            return await self.find_one(plan.id)
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Plan number '{payload.planNo}' already exists in the system.",
            ) from exc
        except Exception as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Backend Error: {str(exc)}. Please check database migrations.",
            ) from exc

    async def find_all(self) -> list[dict]:
        result = await self.db.execute(select(RawMaterialPlan).order_by(desc(RawMaterialPlan.created_at)))
        plans = result.scalars().all()
        return [await self.find_one(plan.id) for plan in plans]

    async def find_one(self, plan_id: str) -> dict | None:
        plan = await self.db.get(RawMaterialPlan, plan_id)
        if not plan:
            return None

        rows_result = await self.db.execute(select(RawMaterialPlanRow).where(RawMaterialPlanRow.plan_id == plan_id))
        rows = rows_result.scalars().all()

        pools_result = await self.db.execute(
            select(RawMaterialPlanPoolDetail).where(RawMaterialPlanPoolDetail.plan_id == plan_id)
        )
        pool_details = pools_result.scalars().all()

        return self._transform_plan(plan, rows, pool_details)

    async def update(self, plan_id: str, payload: CreateRawMaterialPlanDto) -> dict:
        plan = await self.db.get(RawMaterialPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

        data = payload.model_dump()
        plan.plan_no = data["planNo"]
        plan.revision_no = data["revisionNo"]
        plan.ref_production_no = data["refProductionNo"]
        plan.issued_date = self._parse_date(data.get("issuedDate"))
        plan.creator = data.get("issueBy") or plan.creator
        plan.checker = data.get("verifiedBy")

        old_rows = await self.db.execute(select(RawMaterialPlanRow).where(RawMaterialPlanRow.plan_id == plan_id))
        for item in old_rows.scalars().all():
            await self.db.delete(item)

        old_details = await self.db.execute(
            select(RawMaterialPlanPoolDetail).where(RawMaterialPlanPoolDetail.plan_id == plan_id)
        )
        for item in old_details.scalars().all():
            await self.db.delete(item)

        for row in self._build_rows(plan_id, data.get("rows") or []):
            self.db.add(row)
        for detail in self._build_pool_details(plan_id, data.get("poolDetails") or []):
            self.db.add(detail)

        await self.db.commit()
        return await self.find_one(plan_id)

    async def generate_next_plan_no(self) -> str:
        prefix = datetime.now().strftime("RMP-%Y%m%d-")
        result = await self.db.execute(
            select(RawMaterialPlan).where(RawMaterialPlan.plan_no.like(f"{prefix}%")).order_by(desc(RawMaterialPlan.plan_no))
        )
        latest = result.scalars().first()
        if not latest:
            return f"{prefix}001"
        last_number = latest.plan_no.split("-")[-1]
        try:
            value = int(last_number) + 1
        except ValueError:
            value = 1
        return f"{prefix}{str(value).zfill(3)}"

    async def remove(self, plan_id: str) -> dict:
        plan = await self.db.get(RawMaterialPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        data = {
            "id": plan.id,
            "planNo": plan.plan_no,
            "revisionNo": plan.revision_no,
            "refProductionNo": plan.ref_production_no,
        }
        await self.db.delete(plan)
        await self.db.commit()
        return data

    def _build_rows(self, plan_id: str, rows_data: list[dict]) -> list[RawMaterialPlanRow]:
        output: list[RawMaterialPlanRow] = []
        last_valid_date: datetime | None = None
        for row in rows_data:
            current_date = self._parse_date(row.get("date")) if row.get("date") else last_valid_date
            if row.get("date"):
                last_valid_date = current_date
            current_date = current_date or datetime.now()

            output.append(
                RawMaterialPlanRow(
                    id=str(uuid4()),
                    plan_id=plan_id,
                    date=current_date,
                    day_of_week=row.get("dayOfWeek") or "",
                    shift=row.get("shift") or "",
                    grade=row.get("grade"),
                    ratio_uss=self._clean_number(row.get("ratioUSS")),
                    ratio_cl=self._clean_number(row.get("ratioCL")),
                    ratio_bk=self._clean_number(row.get("ratioBK")),
                    product_target=self._clean_number(row.get("productTarget")),
                    cl_consumption=self._clean_number(row.get("clConsumption")),
                    ratio_b_or_c=self._clean_number(row.get("ratioBorC")),
                    plan1_pool=",".join(row.get("plan1Pool")) if isinstance(row.get("plan1Pool"), list) else row.get("plan1Pool"),
                    plan1_note=f"Scoops: {row.get('plan1Scoops') or 0}, Grades: {','.join(row.get('plan1Grades')) if isinstance(row.get('plan1Grades'), list) else (row.get('plan1Grades') or '')}",
                    plan2_pool=",".join(row.get("plan2Pool")) if isinstance(row.get("plan2Pool"), list) else row.get("plan2Pool"),
                    plan2_note=f"Scoops: {row.get('plan2Scoops') or 0}, Grades: {','.join(row.get('plan2Grades')) if isinstance(row.get('plan2Grades'), list) else (row.get('plan2Grades') or '')}",
                    plan3_pool=",".join(row.get("plan3Pool")) if isinstance(row.get("plan3Pool"), list) else row.get("plan3Pool"),
                    plan3_note=f"Scoops: {row.get('plan3Scoops') or 0}, Grades: {','.join(row.get('plan3Grades')) if isinstance(row.get('plan3Grades'), list) else (row.get('plan3Grades') or '')}",
                    cutting_percent=self._clean_number(row.get("cuttingPercent")),
                    cutting_palette=(
                        int(float(row.get("cuttingPalette")))
                        if self._clean_number(row.get("cuttingPalette")) is not None
                        else None
                    ),
                    remarks=row.get("remarks"),
                    special_indicator=row.get("productionMode"),
                )
            )
        return output

    def _build_pool_details(self, plan_id: str, pools_data: list[dict]) -> list[RawMaterialPlanPoolDetail]:
        output: list[RawMaterialPlanPoolDetail] = []
        for pool in pools_data:
            output.append(
                RawMaterialPlanPoolDetail(
                    id=str(uuid4()),
                    plan_id=plan_id,
                    pool_no=pool.get("poolNo") or "",
                    gross_weight=self._clean_number(pool.get("grossWeight")),
                    net_weight=self._clean_number(pool.get("netWeight")),
                    drc=self._clean_number(pool.get("drc")),
                    moisture=self._clean_number(pool.get("moisture")),
                    p0=self._clean_number(pool.get("p0")),
                    pri=self._clean_number(pool.get("pri")),
                    clear_date=self._parse_date(pool.get("clearDate")) if pool.get("clearDate") else None,
                    grade=",".join(pool.get("grade")) if isinstance(pool.get("grade"), list) else pool.get("grade"),
                )
            )
        return output

    def _transform_plan(
        self,
        plan: RawMaterialPlan,
        rows: list[RawMaterialPlanRow],
        pool_details: list[RawMaterialPlanPoolDetail],
    ) -> dict:
        def parse_note(note: str | None) -> dict:
            if not note:
                return {"scoops": 0, "grades": ""}
            scoops = 0
            grades = ""
            try:
                if "Scoops:" in note:
                    scoops_part = note.split("Scoops:")[1].split(",")[0].strip()
                    scoops = int(scoops_part)
                if "Grades:" in note:
                    grades = note.split("Grades:")[1].strip()
            except Exception:
                pass
            return {"scoops": scoops, "grades": grades}

        transformed_rows = []
        for row in rows:
            p1 = parse_note(row.plan1_note)
            p2 = parse_note(row.plan2_note)
            p3 = parse_note(row.plan3_note)
            transformed_rows.append(
                {
                    "id": row.id,
                    "planId": row.plan_id,
                    "date": row.date,
                    "dayOfWeek": row.day_of_week,
                    "shift": row.shift,
                    "grade": row.grade,
                    "ratioUSS": row.ratio_uss,
                    "ratioCL": row.ratio_cl,
                    "ratioBK": row.ratio_bk,
                    "productTarget": row.product_target,
                    "clConsumption": row.cl_consumption,
                    "ratioBorC": row.ratio_b_or_c,
                    "plan1Pool": row.plan1_pool,
                    "plan1Note": row.plan1_note,
                    "plan2Pool": row.plan2_pool,
                    "plan2Note": row.plan2_note,
                    "plan3Pool": row.plan3_pool,
                    "plan3Note": row.plan3_note,
                    "cuttingPercent": row.cutting_percent,
                    "cuttingPalette": row.cutting_palette,
                    "remarks": row.remarks,
                    "specialIndicator": row.special_indicator,
                    "productionMode": row.special_indicator or "normal",
                    "plan1Scoops": p1["scoops"],
                    "plan1Grades": p1["grades"],
                    "plan2Scoops": p2["scoops"],
                    "plan2Grades": p2["grades"],
                    "plan3Scoops": p3["scoops"],
                    "plan3Grades": p3["grades"],
                }
            )

        transformed_pools = [
            {
                "id": item.id,
                "planId": item.plan_id,
                "poolNo": item.pool_no,
                "grossWeight": item.gross_weight,
                "netWeight": item.net_weight,
                "drc": item.drc,
                "moisture": item.moisture,
                "p0": item.p0,
                "pri": item.pri,
                "clearDate": item.clear_date,
                "grade": item.grade,
                "remark": item.remark,
            }
            for item in pool_details
        ]

        return {
            "id": plan.id,
            "planNo": plan.plan_no,
            "revisionNo": plan.revision_no,
            "refProductionNo": plan.ref_production_no,
            "issuedDate": plan.issued_date,
            "creator": plan.creator,
            "checker": plan.checker,
            "status": plan.status,
            "createdAt": plan.created_at,
            "updatedAt": plan.updated_at,
            "rows": transformed_rows,
            "poolDetails": transformed_pools,
        }
