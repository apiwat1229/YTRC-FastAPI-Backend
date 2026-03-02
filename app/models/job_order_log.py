from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobOrderLog(Base):
    __tablename__ = "job_order_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_order_id: Mapped[str] = mapped_column("job_order_id", String, ForeignKey("job_orders.id", ondelete="CASCADE"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    shift: Mapped[str] = mapped_column(String)
    lot_start: Mapped[str] = mapped_column("lot_start", String)
    lot_end: Mapped[str] = mapped_column("lot_end", String)
    quantity: Mapped[int] = mapped_column(Integer)
    sign: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
