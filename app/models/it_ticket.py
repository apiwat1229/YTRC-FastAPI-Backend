from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ITTicket(Base):
    __tablename__ = "it_tickets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    ticket_no: Mapped[str] = mapped_column("ticket_no", String, unique=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String, default="Medium")
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="Open")

    requester_id: Mapped[str] = mapped_column("requester_id", String, ForeignKey("users.id"), index=True)
    assignee_id: Mapped[str | None] = mapped_column("assignee_id", String, ForeignKey("users.id"), nullable=True, index=True)

    is_asset_request: Mapped[bool] = mapped_column("is_asset_request", Boolean, default=False)
    asset_id: Mapped[str | None] = mapped_column("asset_id", String, ForeignKey("it_assets.id"), nullable=True, index=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    expected_date: Mapped[datetime | None] = mapped_column("expected_date", DateTime(timezone=True), nullable=True)
    approver_id: Mapped[str | None] = mapped_column("approver_id", String, nullable=True)

    issued_at: Mapped[datetime | None] = mapped_column("issued_at", DateTime(timezone=True), nullable=True)
    issued_by: Mapped[str | None] = mapped_column("issued_by", String, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column("resolved_at", DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
