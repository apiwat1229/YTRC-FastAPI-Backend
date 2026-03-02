from typing import Any

from pydantic import BaseModel


class CreateRoleDto(BaseModel):
    name: str
    description: str | None = None
    permissions: list[str] | None = None
    icon: str | None = None
    color: str | None = None
    isActive: bool | None = None


class UpdateRoleDto(BaseModel):
    name: str | None = None
    description: str | None = None
    permissions: list[str] | None = None
    icon: str | None = None
    color: str | None = None
    isActive: bool | None = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    permissions: list[str] | Any
    icon: str | None = None
    color: str | None = None
    isActive: bool
    userCount: int | None = None
