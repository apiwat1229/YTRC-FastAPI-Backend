from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    queue_no: Mapped[int] = mapped_column("queue_no", Integer)
    booking_code: Mapped[str] = mapped_column("booking_code", String, unique=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    start_time: Mapped[str] = mapped_column("start_time", String)
    end_time: Mapped[str] = mapped_column("end_time", String)
    slot: Mapped[str | None] = mapped_column(String, nullable=True)

    supplier_id: Mapped[str | None] = mapped_column("supplier_id", String, nullable=True)
    supplier_code: Mapped[str | None] = mapped_column("supplier_code", String, nullable=True)
    supplier_name: Mapped[str | None] = mapped_column("supplier_name", String, nullable=True)

    truck_type: Mapped[str | None] = mapped_column("truck_type", String, nullable=True)
    truck_register: Mapped[str | None] = mapped_column("truck_register", String, nullable=True)

    rubber_type: Mapped[str | None] = mapped_column("rubber_type", String, nullable=True)
    lot_no: Mapped[str | None] = mapped_column("lot_no", String, nullable=True)
    estimated_weight: Mapped[float | None] = mapped_column("estimated_weight", Float, nullable=True)

    moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    drc_est: Mapped[float | None] = mapped_column("drc_est", Float, nullable=True)
    drc_requested: Mapped[float | None] = mapped_column("drc_requested", Float, nullable=True)
    drc_actual: Mapped[float | None] = mapped_column("drc_actual", Float, nullable=True)
    cp_avg: Mapped[float | None] = mapped_column("cp_avg", Float, nullable=True)
    grade: Mapped[str | None] = mapped_column(String, nullable=True)

    recorder: Mapped[str] = mapped_column(String)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    approved_by: Mapped[str | None] = mapped_column("approved_by", String, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column("approved_at", DateTime(timezone=True), nullable=True)

    checkin_at: Mapped[datetime | None] = mapped_column("checkin_at", DateTime(timezone=True), nullable=True)
    checked_in_by: Mapped[str | None] = mapped_column("checked_in_by", String, nullable=True)

    start_drain_at: Mapped[datetime | None] = mapped_column("start_drain_at", DateTime(timezone=True), nullable=True)
    start_drain_by: Mapped[str | None] = mapped_column("start_drain_by", String, nullable=True)
    stop_drain_at: Mapped[datetime | None] = mapped_column("stop_drain_at", DateTime(timezone=True), nullable=True)
    stop_drain_by: Mapped[str | None] = mapped_column("stop_drain_by", String, nullable=True)
    drain_note: Mapped[str | None] = mapped_column("drain_note", Text, nullable=True)

    weight_in: Mapped[float | None] = mapped_column("weight_in", Float, nullable=True)
    weight_in_by: Mapped[str | None] = mapped_column("weight_in_by", String, nullable=True)
    weight_out: Mapped[float | None] = mapped_column("weight_out", Float, nullable=True)
    weight_out_by: Mapped[str | None] = mapped_column("weight_out_by", String, nullable=True)

    rubber_source: Mapped[str | None] = mapped_column("rubber_source", String, nullable=True)

    trailer_weight_in: Mapped[float | None] = mapped_column("trailer_weight_in", Float, nullable=True)
    trailer_weight_out: Mapped[float | None] = mapped_column("trailer_weight_out", Float, nullable=True)
    trailer_rubber_type: Mapped[str | None] = mapped_column("trailer_rubber_type", String, nullable=True)
    trailer_rubber_source: Mapped[str | None] = mapped_column("trailer_rubber_source", String, nullable=True)
    trailer_lot_no: Mapped[str | None] = mapped_column("trailer_lot_no", String, nullable=True)

    trailer_moisture: Mapped[float | None] = mapped_column("trailer_moisture", Float, nullable=True)
    trailer_drc_est: Mapped[float | None] = mapped_column("trailer_drc_est", Float, nullable=True)
    trailer_drc_requested: Mapped[float | None] = mapped_column("trailer_drc_requested", Float, nullable=True)
    trailer_drc_actual: Mapped[float | None] = mapped_column("trailer_drc_actual", Float, nullable=True)
    trailer_cp_avg: Mapped[float | None] = mapped_column("trailer_cp_avg", Float, nullable=True)
    trailer_grade: Mapped[str | None] = mapped_column("trailer_grade", String, nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    deleted_at: Mapped[datetime | None] = mapped_column("deleted_at", DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[str | None] = mapped_column("deleted_by", String, nullable=True)
