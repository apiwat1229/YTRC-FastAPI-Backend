from datetime import datetime

from pydantic import BaseModel


class ShippingPlanItemDto(BaseModel):
    rowId: str
    palletNo: int


class CreateShippingPlanDto(BaseModel):
    planNo: str
    customer: str | None = None
    planDate: str | datetime
    remark: str | None = None
    items: list[ShippingPlanItemDto]
