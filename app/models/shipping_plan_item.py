from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ShippingPlanItem(Base):
    __tablename__ = "shipping_plan_items"
    __table_args__ = (UniqueConstraint("shipping_plan_id", "row_id", "pallet_no", name="uq_shipping_plan_item"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    shipping_plan_id: Mapped[str] = mapped_column(
        "shipping_plan_id", String, ForeignKey("shipping_plans.id", ondelete="CASCADE")
    )
    row_id: Mapped[str] = mapped_column("row_id", String, ForeignKey("production_report_rows.id", ondelete="CASCADE"))
    pallet_no: Mapped[int] = mapped_column("pallet_no", Integer)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
