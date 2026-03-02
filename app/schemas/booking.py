from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CreateBookingDto(BaseModel):
    date: str | datetime
    startTime: str
    endTime: str
    supplierId: str | None = None
    supplierCode: str | None = None
    supplierName: str | None = None
    truckType: str | None = None
    truckRegister: str | None = None
    rubberType: str | None = None
    estimatedWeight: float | str | None = None
    recorder: str | None = None


class UpdateBookingDto(BaseModel):
    supplierId: str | None = None
    supplierCode: str | None = None
    supplierName: str | None = None
    truckType: str | None = None
    truckRegister: str | None = None
    rubberType: str | None = None
    estimatedWeight: float | str | None = None
    recorder: str | None = None
    lotNo: str | None = None
    trailerLotNo: str | None = None
    moisture: float | str | None = None
    drcEst: float | str | None = None
    drcRequested: float | str | None = None
    drcActual: float | str | None = None
    trailerMoisture: float | str | None = None
    trailerDrcEst: float | str | None = None
    trailerDrcRequested: float | str | None = None
    trailerDrcActual: float | str | None = None
    weightIn: float | str | None = None
    weightOut: float | str | None = None
    trailerWeightIn: float | str | None = None
    trailerWeightOut: float | str | None = None
    status: str | None = None
    silent: bool | None = None


class BookingSampleDto(BaseModel):
    id: str | None = None
    sampleNo: int | None = None
    isTrailer: bool | str | None = None

    beforePress: float | str | None = None
    basketWeight: float | str | None = None
    cuplumpWeight: float | str | None = None
    afterPress: float | str | None = None
    percentCp: float | str | None = None

    beforeBaking1: float | str | None = None
    afterDryerB1: float | str | None = None
    beforeLabDryerB1: float | str | None = None
    afterLabDryerB1: float | str | None = None
    drcB1: float | str | None = None
    moisturePercentB1: float | str | None = None
    drcDryB1: float | str | None = None
    labDrcB1: float | str | None = None
    recalDrcB1: float | str | None = None

    beforeBaking2: float | str | None = None
    afterDryerB2: float | str | None = None
    beforeLabDryerB2: float | str | None = None
    afterLabDryerB2: float | str | None = None
    drcB2: float | str | None = None
    moisturePercentB2: float | str | None = None
    drcDryB2: float | str | None = None
    labDrcB2: float | str | None = None
    recalDrcB2: float | str | None = None

    beforeBaking3: float | str | None = None
    afterDryerB3: float | str | None = None
    beforeLabDryerB3: float | str | None = None
    afterLabDryerB3: float | str | None = None
    drcB3: float | str | None = None
    moisturePercentB3: float | str | None = None
    drcDryB3: float | str | None = None
    labDrcB3: float | str | None = None
    recalDrcB3: float | str | None = None

    drc: float | str | None = None
    moistureFactor: float | str | None = None
    recalDrc: float | str | None = None
    difference: float | str | None = None

    p0: float | str | None = None
    p30: float | str | None = None
    pri: float | str | None = None

    storage: str | None = None
    recordedBy: str | None = None


class GenericBodyDto(BaseModel):
    model_config = {"extra": "allow"}
    note: str | None = None


class BookingWeightInDto(BaseModel):
    rubberSource: str | None = None
    rubberType: str | None = None
    weightIn: float | str | None = None
    trailerRubberSource: str | None = None
    trailerRubberType: str | None = None
    trailerWeightIn: float | str | None = None


class BookingWeightOutDto(BaseModel):
    weightOut: float | str | None = None


class BookingDeleteSampleResponse(BaseModel):
    id: str
    bookingId: str | None = None
    sampleNo: int | None = None


class BookingStatsResponse(BaseModel):
    total: int
    checkedIn: int
    pending: int
    slots: dict[str, Any]
