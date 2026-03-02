from pydantic import BaseModel


class CreateCpkAnalysisDto(BaseModel):
    title: str
    lsl: float
    usl: float
    subgroupSize: int
    dataPoints: list[float]
    note: str | None = None
    recordedBy: str | None = None
