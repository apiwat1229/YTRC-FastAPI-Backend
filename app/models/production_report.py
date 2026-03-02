from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProductionReport(Base):
    __tablename__ = "production_reports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    dryer_name: Mapped[str] = mapped_column("dryer_name", String)
    book_no: Mapped[str] = mapped_column("book_no", String)
    page_no: Mapped[str] = mapped_column("page_no", String)
    production_date: Mapped[datetime] = mapped_column("production_date", DateTime(timezone=True))
    shift: Mapped[str] = mapped_column(String)
    grade: Mapped[str] = mapped_column(String)

    ratio_cl: Mapped[float | None] = mapped_column("ratio_cl", Float, nullable=True)
    ratio_uss: Mapped[float | None] = mapped_column("ratio_uss", Float, nullable=True)
    ratio_cutting: Mapped[float | None] = mapped_column("ratio_cutting", Float, nullable=True)

    weight_pallet_remained: Mapped[float | None] = mapped_column("weight_pallet_remained", Float, nullable=True)

    sample_accum_1: Mapped[int | None] = mapped_column("sample_accum_1", Integer, nullable=True)
    sample_accum_2: Mapped[int | None] = mapped_column("sample_accum_2", Integer, nullable=True)
    sample_accum_3: Mapped[int | None] = mapped_column("sample_accum_3", Integer, nullable=True)
    sample_accum_4: Mapped[int | None] = mapped_column("sample_accum_4", Integer, nullable=True)
    sample_accum_5: Mapped[int | None] = mapped_column("sample_accum_5", Integer, nullable=True)

    bale_bag_lot_no: Mapped[str | None] = mapped_column("bale_bag_lot_no", String, nullable=True)

    checked_by: Mapped[str | None] = mapped_column("checked_by", String, nullable=True)
    judged_by: Mapped[str | None] = mapped_column("judged_by", String, nullable=True)
    issued_by: Mapped[str | None] = mapped_column("issued_by", String, nullable=True)
    issued_at: Mapped[datetime | None] = mapped_column("issued_at", DateTime(timezone=True), nullable=True)

    status: Mapped[str] = mapped_column(String, default="DRAFT")

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
