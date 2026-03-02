from datetime import datetime

from pydantic import BaseModel


class ProductionReportRowDto(BaseModel):
    startTime: str
    palletType: str
    lotNo: str
    weight1: float | None = None
    weight2: float | None = None
    weight3: float | None = None
    weight4: float | None = None
    weight5: float | None = None
    sampleCount: int | None = None
    weight1Status: str | None = None
    weight2Status: str | None = None
    weight3Status: str | None = None
    weight4Status: str | None = None
    weight5Status: str | None = None
    sampleStatus: str | None = None


class CreateProductionReportDto(BaseModel):
    dryerName: str
    bookNo: str
    pageNo: str
    productionDate: str | datetime
    shift: str
    grade: str
    ratioCL: float | None = None
    ratioUSS: float | None = None
    ratioCutting: float | None = None
    weightPalletRemained: float | None = None
    sampleAccum1: int | None = None
    sampleAccum2: int | None = None
    sampleAccum3: int | None = None
    sampleAccum4: int | None = None
    sampleAccum5: int | None = None
    rows: list[ProductionReportRowDto]
    baleBagLotNo: str | None = None
    checkedBy: str | None = None
    judgedBy: str | None = None
    issuedBy: str | None = None
    issuedAt: str | datetime | None = None
    status: str | None = None
