from datetime import datetime

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeBook(Base):
    __tablename__ = "knowledge_books"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String, index=True)
    file_type: Mapped[str] = mapped_column("file_type", String)
    file_path: Mapped[str] = mapped_column("file_path", String)
    file_name: Mapped[str] = mapped_column("file_name", String)
    file_size: Mapped[int] = mapped_column("file_size", Integer)
    cover_image: Mapped[str | None] = mapped_column("cover_image", String, nullable=True)
    author: Mapped[str | None] = mapped_column(String, nullable=True)
    uploaded_by: Mapped[str] = mapped_column("uploaded_by", String, ForeignKey("users.id"), index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    downloads: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    is_published: Mapped[bool] = mapped_column("is_published", Boolean, default=True, index=True)
    training_date: Mapped[datetime | None] = mapped_column("training_date", DateTime(timezone=True), nullable=True)
    attendees: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
