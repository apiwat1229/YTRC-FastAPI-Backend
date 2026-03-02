from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

notification_group_members = Table(
    "_NotificationGroupMembers",
    Base.metadata,
    Column("A", String, ForeignKey("NotificationGroup.id", ondelete="CASCADE"), primary_key=True),
    Column("B", String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class NotificationGroup(Base):
    __tablename__ = "NotificationGroup"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    icon: Mapped[str | None] = mapped_column(String, nullable=True)
    color: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updatedAt", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    members = relationship("User", secondary=notification_group_members, back_populates="notification_groups")
