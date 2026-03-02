from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RawMaterialPlanPoolDetail(Base):
    __tablename__ = "raw_material_plan_pool_details"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    plan_id: Mapped[str] = mapped_column("plan_id", String, ForeignKey("raw_material_plans.id", ondelete="CASCADE"))

    pool_no: Mapped[str] = mapped_column("pool_no", String)
    gross_weight: Mapped[float | None] = mapped_column("gross_weight", Float, nullable=True)
    net_weight: Mapped[float | None] = mapped_column("net_weight", Float, nullable=True)
    drc: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    p0: Mapped[float | None] = mapped_column(Float, nullable=True)
    pri: Mapped[float | None] = mapped_column(Float, nullable=True)
    clear_date: Mapped[datetime | None] = mapped_column("clear_date", DateTime(timezone=True), nullable=True)
    grade: Mapped[str | None] = mapped_column(String, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
