from datetime import datetime

from pydantic import BaseModel


class CreateKnowledgeBookDto(BaseModel):
    title: str
    description: str | None = None
    category: str
    fileType: str
    fileName: str
    filePath: str
    fileSize: int
    coverImage: str | None = None
    author: str | None = None
    tags: list[str] | None = []
    uploadedBy: str
    trainingDate: str | datetime | None = None
    attendees: int | None = 0


class UpdateKnowledgeBookDto(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    author: str | None = None
    tags: list[str] | None = None
    isPublished: bool | None = None
    trainingDate: str | datetime | None = None
    attendees: int | None = None
