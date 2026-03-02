from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BookingLabSample(Base):
    __tablename__ = "booking_lab_samples"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    booking_id: Mapped[str] = mapped_column("booking_id", String, ForeignKey("bookings.id", ondelete="CASCADE"))
    sample_no: Mapped[int] = mapped_column("sample_no", Integer)
    is_trailer: Mapped[bool] = mapped_column("is_trailer", Boolean, default=False)

    before_press: Mapped[float | None] = mapped_column("before_press", Float, nullable=True)
    basket_weight: Mapped[float | None] = mapped_column("basket_weight", Float, nullable=True)
    cuplump_weight: Mapped[float | None] = mapped_column("cuplump_weight", Float, nullable=True)
    after_press: Mapped[float | None] = mapped_column("after_press", Float, nullable=True)
    percent_cp: Mapped[float | None] = mapped_column("percent_cp", Float, nullable=True)

    before_baking_1: Mapped[float | None] = mapped_column("before_baking_1", Float, nullable=True)
    after_dryer_b1: Mapped[float | None] = mapped_column("after_dryer_b1", Float, nullable=True)
    before_lab_dryer_b1: Mapped[float | None] = mapped_column("before_lab_dryer_b1", Float, nullable=True)
    after_lab_dryer_b1: Mapped[float | None] = mapped_column("after_lab_dryer_b1", Float, nullable=True)
    drc_b1: Mapped[float | None] = mapped_column("drc_b1", Float, nullable=True)
    moisture_percent_b1: Mapped[float | None] = mapped_column("moisture_percent_b1", Float, nullable=True)
    drc_dry_b1: Mapped[float | None] = mapped_column("drc_dry_b1", Float, nullable=True)
    lab_drc_b1: Mapped[float | None] = mapped_column("lab_drc_b1", Float, nullable=True)
    recal_drc_b1: Mapped[float | None] = mapped_column("recal_drc_b1", Float, nullable=True)

    before_baking_2: Mapped[float | None] = mapped_column("before_baking_2", Float, nullable=True)
    after_dryer_b2: Mapped[float | None] = mapped_column("after_dryer_b2", Float, nullable=True)
    before_lab_dryer_b2: Mapped[float | None] = mapped_column("before_lab_dryer_b2", Float, nullable=True)
    after_lab_dryer_b2: Mapped[float | None] = mapped_column("after_lab_dryer_b2", Float, nullable=True)
    drc_b2: Mapped[float | None] = mapped_column("drc_b2", Float, nullable=True)
    moisture_percent_b2: Mapped[float | None] = mapped_column("moisture_percent_b2", Float, nullable=True)
    drc_dry_b2: Mapped[float | None] = mapped_column("drc_dry_b2", Float, nullable=True)
    lab_drc_b2: Mapped[float | None] = mapped_column("lab_drc_b2", Float, nullable=True)
    recal_drc_b2: Mapped[float | None] = mapped_column("recal_drc_b2", Float, nullable=True)

    before_baking_3: Mapped[float | None] = mapped_column("before_baking_3", Float, nullable=True)
    after_dryer_b3: Mapped[float | None] = mapped_column("after_dryer_b3", Float, nullable=True)
    before_lab_dryer_b3: Mapped[float | None] = mapped_column("before_lab_dryer_b3", Float, nullable=True)
    after_lab_dryer_b3: Mapped[float | None] = mapped_column("after_lab_dryer_b3", Float, nullable=True)
    drc_b3: Mapped[float | None] = mapped_column("drc_b3", Float, nullable=True)
    moisture_percent_b3: Mapped[float | None] = mapped_column("moisture_percent_b3", Float, nullable=True)
    drc_dry_b3: Mapped[float | None] = mapped_column("drc_dry_b3", Float, nullable=True)
    lab_drc_b3: Mapped[float | None] = mapped_column("lab_drc_b3", Float, nullable=True)
    recal_drc_b3: Mapped[float | None] = mapped_column("recal_drc_b3", Float, nullable=True)

    drc: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_factor: Mapped[float | None] = mapped_column("moisture_factor", Float, nullable=True)
    recal_drc: Mapped[float | None] = mapped_column("recal_drc", Float, nullable=True)
    difference: Mapped[float | None] = mapped_column(Float, nullable=True)

    p0: Mapped[float | None] = mapped_column(Float, nullable=True)
    p30: Mapped[float | None] = mapped_column(Float, nullable=True)
    pri: Mapped[float | None] = mapped_column(Float, nullable=True)

    storage: Mapped[str | None] = mapped_column(String, nullable=True)
    recorded_by: Mapped[str | None] = mapped_column("recorded_by", String, nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
