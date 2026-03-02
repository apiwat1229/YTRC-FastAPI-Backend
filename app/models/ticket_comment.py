from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    ticket_id: Mapped[str] = mapped_column("ticket_id", String, ForeignKey("it_tickets.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column("user_id", String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
