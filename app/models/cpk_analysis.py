from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CpkAnalysis(Base):
    __tablename__ = "cpk_analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    lsl: Mapped[float] = mapped_column(Float)
    usl: Mapped[float] = mapped_column(Float)
    subgroup_size: Mapped[int] = mapped_column("subgroup_size", Integer)
    data_points: Mapped[list[float]] = mapped_column("data_points", ARRAY(Float))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    recorded_by: Mapped[str | None] = mapped_column("recorded_by", String, nullable=True)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
