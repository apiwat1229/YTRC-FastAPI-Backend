from pydantic import BaseModel


class CreatePostDto(BaseModel):
    title: str
    content: str | None = None
    published: bool | None = None


class UpdatePostDto(BaseModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None
