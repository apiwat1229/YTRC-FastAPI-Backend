from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, model_validator


def clean_empty_strings_from_dict(data: Any) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            if value == "" or value == "undefined" or value == "null":
                # Convert empty string/null string representations to None
                data[key] = None
    return data


class CreateSupplierDto(BaseModel):
    code: str
    name: str
    firstName: str | None = None
    lastName: str | None = None
    title: str | None = None
    taxId: str | None = None
    address: str | None = None
    provinceId: int | None = None
    districtId: int | None = None
    subdistrictId: int | None = None
    zipCode: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    status: str | None = None
    avatar: str | None = None
    certificateNumber: str | None = None
    certificateExpire: datetime | None = None
    score: float | None = None
    eudrQuotaUsed: float | None = None
    eudrQuotaCurrent: float | None = None
    rubberTypeCodes: list[str] | None = None
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def clean_empty_strings(cls, data: Any) -> Any:
        return clean_empty_strings_from_dict(data)


class UpdateSupplierDto(BaseModel):
    code: str | None = None
    name: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    title: str | None = None
    taxId: str | None = None
    address: str | None = None
    provinceId: int | None = None
    districtId: int | None = None
    subdistrictId: int | None = None
    zipCode: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    status: str | None = None
    avatar: str | None = None
    certificateNumber: str | None = None
    certificateExpire: datetime | None = None
    score: float | None = None
    eudrQuotaUsed: float | None = None
    eudrQuotaCurrent: float | None = None
    rubberTypeCodes: list[str] | None = None
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def clean_empty_strings(cls, data: Any) -> Any:
        return clean_empty_strings_from_dict(data)
