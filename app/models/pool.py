from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Pool(Base):
    __tablename__ = "pools"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="empty")
    grade: Mapped[str | None] = mapped_column(String, nullable=True)
    rubber_type: Mapped[str | None] = mapped_column("rubber_type", String, nullable=True)
    capacity: Mapped[float] = mapped_column(Float, default=3000)
    total_weight: Mapped[float] = mapped_column("total_weight", Float, default=0)
    total_gross_weight: Mapped[float] = mapped_column("total_gross_weight", Float, default=0)

    open_date: Mapped[datetime | None] = mapped_column("open_date", DateTime(timezone=True), nullable=True)
    close_date: Mapped[datetime | None] = mapped_column("close_date", DateTime(timezone=True), nullable=True)
    empty_date: Mapped[datetime | None] = mapped_column("empty_date", DateTime(timezone=True), nullable=True)
    filling_date: Mapped[datetime | None] = mapped_column("filling_date", DateTime(timezone=True), nullable=True)

    production_plan: Mapped[str | None] = mapped_column("production_plan", String, nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
