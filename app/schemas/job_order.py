from datetime import datetime

from pydantic import BaseModel


class JobOrderLogDto(BaseModel):
    date: str | datetime
    shift: str
    lotStart: str
    lotEnd: str
    quantity: int
    sign: str | None = None


class CreateJobOrderDto(BaseModel):
    bookNo: str
    no: int
    jobOrderNo: str
    contractNo: str
    grade: str
    otherGrade: str | None = None
    quantityBale: int
    palletType: str
    orderQuantity: int
    palletMarking: bool | None = True
    note: str | None = None
    qaName: str
    qaDate: str | datetime
    logs: list[JobOrderLogDto] | None = None


class UpdateJobOrderDto(BaseModel):
    bookNo: str | None = None
    no: int | None = None
    jobOrderNo: str | None = None
    contractNo: str | None = None
    grade: str | None = None
    otherGrade: str | None = None
    quantityBale: int | None = None
    palletType: str | None = None
    orderQuantity: int | None = None
    palletMarking: bool | None = None
    note: str | None = None
    qaName: str | None = None
    qaDate: str | datetime | None = None
    isClosed: bool | None = None
    productionName: str | None = None
    productionDate: str | datetime | None = None
    logs: list[JobOrderLogDto] | None = None
