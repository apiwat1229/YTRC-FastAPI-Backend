from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApprovalLog(Base):
    __tablename__ = "approval_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    approval_request_id: Mapped[str] = mapped_column("approval_request_id", String, ForeignKey("approval_requests.id"))

    action: Mapped[str] = mapped_column(String)
    old_value: Mapped[Any | None] = mapped_column("old_value", JSONB, nullable=True)
    new_value: Mapped[Any | None] = mapped_column("new_value", JSONB, nullable=True)

    actor_id: Mapped[str] = mapped_column("actor_id", String)
    actor_name: Mapped[str] = mapped_column("actor_name", String)
    actor_role: Mapped[str] = mapped_column("actor_role", String)

    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column("ip_address", String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column("user_agent", Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
