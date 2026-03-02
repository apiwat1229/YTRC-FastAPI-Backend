from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PoolItem(Base):
    __tablename__ = "pool_items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    pool_id: Mapped[str] = mapped_column("pool_id", String, ForeignKey("pools.id", ondelete="CASCADE"))

    booking_id: Mapped[str] = mapped_column("booking_id", String)
    lot_number: Mapped[str] = mapped_column("lot_number", String)
    supplier_name: Mapped[str] = mapped_column("supplier_name", String)
    supplier_code: Mapped[str] = mapped_column("supplier_code", String)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    net_weight: Mapped[float] = mapped_column("net_weight", Float)
    gross_weight: Mapped[float] = mapped_column("gross_weight", Float)
    grade: Mapped[str] = mapped_column(String)
    rubber_type: Mapped[str] = mapped_column("rubber_type", String)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
