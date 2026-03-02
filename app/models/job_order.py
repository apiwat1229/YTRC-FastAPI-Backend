from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobOrder(Base):
    __tablename__ = "job_orders"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    book_no: Mapped[str] = mapped_column("book_no", String)
    no: Mapped[int] = mapped_column(Integer)
    job_order_no: Mapped[str] = mapped_column("job_order_no", String, unique=True)
    contract_no: Mapped[str] = mapped_column("contract_no", String)
    grade: Mapped[str] = mapped_column(String)
    other_grade: Mapped[str | None] = mapped_column("other_grade", String, nullable=True)
    quantity_bale: Mapped[int] = mapped_column("quantity_bale", Integer)
    pallet_type: Mapped[str] = mapped_column("pallet_type", String)
    order_quantity: Mapped[int] = mapped_column("order_quantity", Integer)
    pallet_marking: Mapped[bool] = mapped_column("pallet_marking", Boolean, default=True)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
    qa_name: Mapped[str] = mapped_column("qa_name", String)
    qa_date: Mapped[datetime] = mapped_column("qa_date", DateTime(timezone=True))
    is_closed: Mapped[bool] = mapped_column("is_closed", Boolean, default=False)
    production_name: Mapped[str | None] = mapped_column("production_name", String, nullable=True)
    production_date: Mapped[datetime | None] = mapped_column("production_date", DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
