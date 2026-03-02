from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    request_type: Mapped[str] = mapped_column("request_type", String)
    entity_type: Mapped[str] = mapped_column("entity_type", String)
    entity_id: Mapped[str] = mapped_column("entity_id", String)

    source_app: Mapped[str] = mapped_column("source_app", String)
    action_type: Mapped[str] = mapped_column("action_type", String)

    current_data: Mapped[Any | None] = mapped_column("current_data", JSONB, nullable=True)
    proposed_data: Mapped[Any | None] = mapped_column("proposed_data", JSONB, nullable=True)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String, default="NORMAL")
    status: Mapped[str] = mapped_column(String, default="PENDING")

    requester_id: Mapped[str] = mapped_column("requester_id", String, ForeignKey("users.id"))
    approver_id: Mapped[str | None] = mapped_column("approver_id", String, ForeignKey("users.id"), nullable=True)

    submitted_at: Mapped[datetime] = mapped_column("submitted_at", DateTime(timezone=True), server_default=func.now())
    acted_at: Mapped[datetime | None] = mapped_column("acted_at", DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column("expires_at", DateTime(timezone=True), nullable=True)

    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column("deleted_at", DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[str | None] = mapped_column("deleted_by", String, nullable=True)
