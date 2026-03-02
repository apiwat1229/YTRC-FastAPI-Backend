from datetime import datetime

from pydantic import BaseModel


class CreateITAssetDto(BaseModel):
    code: str
    name: str
    category: str
    stock: int | None = 0
    minStock: int | None = 2
    location: str | None = None
    description: str | None = None
    image: str | None = None
    price: float | None = 0
    receivedDate: datetime | str | None = None
    receiver: str | None = None
    serialNumber: str | None = None
    barcode: str | None = None


class UpdateITAssetDto(BaseModel):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    stock: int | None = None
    minStock: int | None = None
    location: str | None = None
    description: str | None = None
    image: str | None = None
    price: float | None = None
    receivedDate: datetime | str | None = None
    receiver: str | None = None
    serialNumber: str | None = None
    barcode: str | None = None
