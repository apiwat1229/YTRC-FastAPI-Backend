from datetime import datetime

from pydantic import BaseModel


class CreateITTicketDto(BaseModel):
    title: str
    description: str | None = None
    category: str
    priority: str | None = "Medium"
    location: str | None = None
    assetId: str | None = None
    quantity: int | None = 0
    expectedDate: str | datetime | None = None
    approverId: str | None = None
    isAssetRequest: bool | None = False
    createdAt: str | datetime | None = None


class UpdateITTicketDto(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: str | None = None
    status: str | None = None
    location: str | None = None
    assigneeId: str | None = None
    assetId: str | None = None
    quantity: int | None = None
    expectedDate: str | datetime | None = None
    approverId: str | None = None
    isAssetRequest: bool | None = None
    issuedBy: str | None = None
    createdAt: str | datetime | None = None
    resolvedAt: str | datetime | None = None


class CreateTicketCommentDto(BaseModel):
    content: str
