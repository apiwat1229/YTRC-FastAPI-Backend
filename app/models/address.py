from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    name_th: Mapped[str] = mapped_column(String)
    name_en: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

    districts = relationship("District", back_populates="province")


class District(Base):
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    province_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id"))
    code: Mapped[str] = mapped_column(String, unique=True)
    name_th: Mapped[str] = mapped_column(String)
    name_en: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

    province = relationship("Province", back_populates="districts")
    subdistricts = relationship("Subdistrict", back_populates="district")


class Subdistrict(Base):
    __tablename__ = "subdistricts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(Integer, ForeignKey("districts.id"))
    code: Mapped[str] = mapped_column(String, unique=True)
    name_th: Mapped[str] = mapped_column(String)
    name_en: Mapped[str] = mapped_column(String)
    zip_code: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())

    district = relationship("District", back_populates="subdistricts")
