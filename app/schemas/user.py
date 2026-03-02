from typing import Any

from pydantic import BaseModel, EmailStr


class CreateUserDto(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    displayName: str | None = None
    department: str | None = None
    position: str | None = None
    role: str | None = None
    status: str | None = None
    employeeId: str | None = None
    pinCode: str | None = None
    avatar: str | None = None
    roleId: str | None = None
    forceChangePassword: bool | None = None
    signatureText: str | None = None
    signatureStyle: str | None = None


class UpdateUserDto(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    displayName: str | None = None
    department: str | None = None
    position: str | None = None
    role: str | None = None
    status: str | None = None
    pinCode: str | None = None
    employeeId: str | None = None
    hodId: str | None = None
    avatar: str | None = None
    forceChangePassword: bool | None = None
    preferences: Any | None = None
    signatureText: str | None = None
    signatureStyle: str | None = None
    roleId: str | None = None
