from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_app: Mapped[str] = mapped_column("sourceApp", String)
    action_type: Mapped[str] = mapped_column("actionType", String)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True)

    recipient_roles: Mapped[Any] = mapped_column("recipientRoles", JSONB, default=list)
    recipient_groups: Mapped[Any] = mapped_column("recipientGroups", JSONB, default=list)
    recipient_users: Mapped[Any] = mapped_column("recipientUsers", JSONB, default=list)
    channels: Mapped[Any] = mapped_column("channels", JSONB, default=lambda: ["IN_APP"])

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
