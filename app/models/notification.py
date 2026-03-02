from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String, default="INFO")
    status: Mapped[str] = mapped_column(String, default="UNREAD")

    user_id: Mapped[str] = mapped_column("user_id", String, index=True)
    source_app: Mapped[str] = mapped_column("sourceApp", String)
    action_type: Mapped[str] = mapped_column("actionType", String)
    entity_id: Mapped[str | None] = mapped_column("entityId", String, nullable=True)
    action_url: Mapped[str | None] = mapped_column("actionUrl", String, nullable=True)
    metadata_json: Mapped[Any | None] = mapped_column("metadata", JSONB, nullable=True)

    approval_request_id: Mapped[str | None] = mapped_column("approval_request_id", String, nullable=True)
    approval_status: Mapped[str | None] = mapped_column("approval_status", String, nullable=True)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
