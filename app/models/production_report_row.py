from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProductionReportRow(Base):
    __tablename__ = "production_report_rows"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    report_id: Mapped[str] = mapped_column("report_id", String, ForeignKey("production_reports.id", ondelete="CASCADE"))

    start_time: Mapped[str] = mapped_column("start_time", String)
    pallet_type: Mapped[str] = mapped_column("pallet_type", String)
    lot_no: Mapped[str] = mapped_column("lot_no", String)

    weight_1: Mapped[float | None] = mapped_column("weight_1", Float, nullable=True)
    weight_2: Mapped[float | None] = mapped_column("weight_2", Float, nullable=True)
    weight_3: Mapped[float | None] = mapped_column("weight_3", Float, nullable=True)
    weight_4: Mapped[float | None] = mapped_column("weight_4", Float, nullable=True)
    weight_5: Mapped[float | None] = mapped_column("weight_5", Float, nullable=True)

    sample_count: Mapped[int | None] = mapped_column("sample_count", Integer, nullable=True)

    weight_1_status: Mapped[str | None] = mapped_column("weight_1_status", String, nullable=True)
    weight_2_status: Mapped[str | None] = mapped_column("weight_2_status", String, nullable=True)
    weight_3_status: Mapped[str | None] = mapped_column("weight_3_status", String, nullable=True)
    weight_4_status: Mapped[str | None] = mapped_column("weight_4_status", String, nullable=True)
    weight_5_status: Mapped[str | None] = mapped_column("weight_5_status", String, nullable=True)
    sample_status: Mapped[str | None] = mapped_column("sample_status", String, nullable=True)
