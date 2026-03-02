from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.address import District, Province, Subdistrict


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column("display_name", String)

    tax_id: Mapped[str | None] = mapped_column("tax_id", String, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)

    province_id: Mapped[int | None] = mapped_column("province_id", Integer, ForeignKey("provinces.id"), nullable=True)
    district_id: Mapped[int | None] = mapped_column("district_id", Integer, ForeignKey("districts.id"), nullable=True)
    subdistrict_id: Mapped[int | None] = mapped_column(
        "subdistrict_id", Integer, ForeignKey("subdistricts.id"), nullable=True
    )

    province = relationship("Province", lazy="joined")
    district = relationship("District", lazy="joined")
    subdistrict = relationship("Subdistrict", lazy="joined")

    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rubber_type_codes: Mapped[list[str]] = mapped_column("rubber_type_codes", ARRAY(String), default=list)

    first_name: Mapped[str | None] = mapped_column("first_name", String, nullable=True)
    last_name: Mapped[str | None] = mapped_column("last_name", String, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    zip_code: Mapped[str | None] = mapped_column("zip_code", String, nullable=True)

    certificate_number: Mapped[str | None] = mapped_column("certificate_number", String, nullable=True)
    certificate_expire: Mapped[datetime | None] = mapped_column("certificate_expire", DateTime(timezone=True), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    eudr_quota_used: Mapped[float | None] = mapped_column("eudr_quota_used", Float, nullable=True)
    eudr_quota_current: Mapped[float | None] = mapped_column("eudr_quota_current", Float, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column("deleted_at", DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[str | None] = mapped_column("deleted_by", String, nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
