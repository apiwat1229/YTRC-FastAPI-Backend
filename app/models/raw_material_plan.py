from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RawMaterialPlan(Base):
    __tablename__ = "raw_material_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    plan_no: Mapped[str] = mapped_column("plan_no", String, unique=True)
    revision_no: Mapped[str] = mapped_column("revision_no", String)
    ref_production_no: Mapped[str] = mapped_column("ref_production_no", String)
    issued_date: Mapped[datetime] = mapped_column("issued_date", DateTime(timezone=True))

    creator: Mapped[str] = mapped_column(String)
    checker: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="DRAFT")

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
