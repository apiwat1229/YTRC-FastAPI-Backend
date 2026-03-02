from typing import Literal

from pydantic import BaseModel


class BroadcastDto(BaseModel):
    title: str
    message: str
    type: Literal["INFO", "SUCCESS", "WARNING", "ERROR"] | None = None
    recipientRoles: list[str] | None = None
    recipientUsers: list[str] | None = None
    recipientGroups: list[str] | None = None
    actionUrl: str | None = None


class UpdateNotificationSettingDto(BaseModel):
    sourceApp: str
    actionType: str
    isActive: bool | None = None
    recipientRoles: list[str] | None = None
    recipientUsers: list[str] | None = None
    recipientGroups: list[str] | None = None
    channels: list[str] | None = None


class DeleteBroadcastsDto(BaseModel):
    ids: list[str]
