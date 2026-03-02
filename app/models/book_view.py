from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BookView(Base):
    __tablename__ = "book_views"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    book_id: Mapped[str] = mapped_column("book_id", String, ForeignKey("knowledge_books.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column("user_id", String, ForeignKey("users.id"), index=True)
    viewed_at: Mapped[datetime] = mapped_column("viewed_at", DateTime(timezone=True), server_default=func.now())
