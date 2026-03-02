from datetime import datetime

from pydantic import BaseModel


class RawMaterialPlanRowDto(BaseModel):
    date: datetime | str | None = None
    dayOfWeek: str
    shift: str
    productionMode: str | None = None
    grade: str | None = None

    ratioUSS: float | str | None = None
    ratioCL: float | str | None = None
    ratioBK: float | str | None = None
    productTarget: float | str | None = None
    clConsumption: float | str | None = None
    ratioBorC: float | str | None = None

    plan1Pool: list[str] | str | None = None
    plan1Scoops: int | None = None
    plan1Grades: list[str] | str | None = None

    plan2Pool: list[str] | str | None = None
    plan2Scoops: int | None = None
    plan2Grades: list[str] | str | None = None

    plan3Pool: list[str] | str | None = None
    plan3Scoops: int | None = None
    plan3Grades: list[str] | str | None = None

    cuttingPercent: float | str | None = None
    cuttingPalette: float | str | None = None
    remarks: str | None = None


class RawMaterialPlanPoolDetailDto(BaseModel):
    poolNo: str
    grossWeight: float | str | None = None
    netWeight: float | str | None = None
    drc: float | str | None = None
    moisture: float | str | None = None
    p0: float | str | None = None
    pri: float | str | None = None
    clearDate: datetime | str | None = None
    grade: list[str] | str | None = None


class CreateRawMaterialPlanDto(BaseModel):
    planNo: str
    revisionNo: str
    refProductionNo: str
    issuedDate: datetime | str | None = None

    rows: list[RawMaterialPlanRowDto]
    poolDetails: list[RawMaterialPlanPoolDetailDto]

    issueBy: str | None = None
    verifiedBy: str | None = None
    status: str | None = None
