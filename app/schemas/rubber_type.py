from pydantic import BaseModel


class CreateRubberTypeDto(BaseModel):
    code: str
    name: str
    category: str | None = None
    description: str | None = None
    status: str | None = None
    is_active: bool | None = None


class UpdateRubberTypeDto(BaseModel):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    description: str | None = None
    status: str | None = None
    is_active: bool | None = None
