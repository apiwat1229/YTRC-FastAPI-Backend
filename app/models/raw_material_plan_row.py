from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RawMaterialPlanRow(Base):
    __tablename__ = "raw_material_plan_rows"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    plan_id: Mapped[str] = mapped_column("plan_id", String, ForeignKey("raw_material_plans.id", ondelete="CASCADE"))

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    day_of_week: Mapped[str] = mapped_column("day_of_week", String)
    shift: Mapped[str] = mapped_column(String)
    grade: Mapped[str | None] = mapped_column(String, nullable=True)

    ratio_uss: Mapped[float | None] = mapped_column("ratio_uss", Float, nullable=True)
    ratio_cl: Mapped[float | None] = mapped_column("ratio_cl", Float, nullable=True)
    ratio_bk: Mapped[float | None] = mapped_column("ratio_bk", Float, nullable=True)
    product_target: Mapped[float | None] = mapped_column("product_target", Float, nullable=True)
    cl_consumption: Mapped[float | None] = mapped_column("cl_consumption", Float, nullable=True)
    ratio_b_or_c: Mapped[float | None] = mapped_column("ratio_b_or_c", Float, nullable=True)

    plan1_pool: Mapped[str | None] = mapped_column("plan1_pool", String, nullable=True)
    plan1_note: Mapped[str | None] = mapped_column("plan1_note", Text, nullable=True)
    plan2_pool: Mapped[str | None] = mapped_column("plan2_pool", String, nullable=True)
    plan2_note: Mapped[str | None] = mapped_column("plan2_note", Text, nullable=True)
    plan3_pool: Mapped[str | None] = mapped_column("plan3_pool", String, nullable=True)
    plan3_note: Mapped[str | None] = mapped_column("plan3_note", Text, nullable=True)

    cutting_percent: Mapped[float | None] = mapped_column("cutting_percent", Float, nullable=True)
    cutting_palette: Mapped[int | None] = mapped_column("cutting_palette", Integer, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    special_indicator: Mapped[str | None] = mapped_column("special_indicator", String, nullable=True)
