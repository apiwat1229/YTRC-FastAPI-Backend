from pydantic import BaseModel


class NotificationGroupCreateDto(BaseModel):
    name: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    memberIds: list[str] | None = None


class NotificationGroupUpdateDto(BaseModel):
    name: str | None = None
    description: str | None = None
    isActive: bool | None = None
    icon: str | None = None
    color: str | None = None
    memberIds: list[str] | None = None


class NotificationGroupAddMembersDto(BaseModel):
    userIds: list[str]
