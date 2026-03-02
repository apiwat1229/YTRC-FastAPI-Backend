from datetime import datetime

from pydantic import BaseModel


class PoolCreateDto(BaseModel):
    name: str
    status: str | None = None
    grade: str | None = None
    rubberType: str | None = None
    capacity: float | None = None


class PoolUpdateDto(BaseModel):
    name: str | None = None
    status: str | None = None
    grade: str | None = None
    rubberType: str | None = None
    capacity: float | None = None
    totalWeight: float | None = None
    totalGrossWeight: float | None = None
    closeDate: datetime | None = None
    fillingDate: datetime | None = None


class PoolItemDto(BaseModel):
    id: str | None = None
    booking_id: str | None = None
    lot_number: str | None = None
    supplier_name: str | None = None
    supplier_code: str | None = None
    date: datetime | str | None = None
    net_weight: float | str | None = None
    gross_weight: float | str | None = None
    displayWeight: float | str | None = None
    weightIn: float | str | None = None
    grade: str | None = None
    rubber_type: str | None = None
    displayRubberType: str | None = None
