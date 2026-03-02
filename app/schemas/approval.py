from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class CreateApprovalRequestDto(BaseModel):
    requestType: str
    entityType: str
    entityId: str
    sourceApp: str
    actionType: str
    currentData: Any | None = None
    proposedData: Any | None = None
    reason: str | None = None
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] | None = None
    expiresAt: datetime | None = None


class ApproveDto(BaseModel):
    remark: str | None = None


class RejectDto(BaseModel):
    remark: str


class ReturnDto(BaseModel):
    remark: str


class CancelDto(BaseModel):
    reason: str | None = None


class VoidDto(BaseModel):
    reason: str
