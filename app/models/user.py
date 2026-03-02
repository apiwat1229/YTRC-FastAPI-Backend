from datetime import datetime
from typing import Any

from sqlalchemy import (Boolean, DateTime, ForeignKey, Integer, String, Text,
                        func)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.notification_group import notification_group_members


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    password: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String, default="staff_1")

    first_name: Mapped[str | None] = mapped_column("first_name", String, nullable=True)
    last_name: Mapped[str | None] = mapped_column("last_name", String, nullable=True)
    display_name: Mapped[str | None] = mapped_column("display_name", String, nullable=True)
    department: Mapped[str | None] = mapped_column(String, nullable=True)
    position: Mapped[str | None] = mapped_column(String, nullable=True)
    employee_id: Mapped[str | None] = mapped_column("employee_id", String, unique=True, nullable=True)

    status: Mapped[str] = mapped_column(String, default="ACTIVE")
    pin_code: Mapped[str | None] = mapped_column("pin_code", String, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    permissions: Mapped[Any] = mapped_column(JSONB, default=list)
    preferences: Mapped[Any | None] = mapped_column(JSONB, nullable=True)

    force_change_password: Mapped[bool] = mapped_column("force_change_password", Boolean, default=False)
    failed_login_attempts: Mapped[int] = mapped_column("failed_login_attempts", Integer, default=0)
    last_login_at: Mapped[datetime | None] = mapped_column("last_login_at", DateTime(timezone=True), nullable=True)

    signature_text: Mapped[str | None] = mapped_column("signature_text", String, nullable=True)
    signature_style: Mapped[str | None] = mapped_column("signature_style", String, nullable=True)

    role_id: Mapped[str | None] = mapped_column("role_id", String, ForeignKey("roles.id"), nullable=True)
    role_record = relationship("Role", back_populates="users", lazy="joined")
    notification_groups = relationship(
        "NotificationGroup",
        secondary=notification_group_members,
        back_populates="members",
    )

    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
