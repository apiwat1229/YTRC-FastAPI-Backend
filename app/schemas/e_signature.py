from pydantic import BaseModel


class CreateESignatureDto(BaseModel):
    employeeId: str
    signature: str
    status: bool | None = True


class UpdateESignatureDto(BaseModel):
    employeeId: str | None = None
    signature: str | None = None
    status: bool | None = None
