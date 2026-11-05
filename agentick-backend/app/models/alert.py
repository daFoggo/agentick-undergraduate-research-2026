import uuid

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Alert(Base, TimestampMixin):
    """A sprint-risk alert published by the offline job for one Plane work item."""

    __tablename__ = "alerts"

    work_item_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)  # Plane's own work item id
    project_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    issue_key: Mapped[str] = mapped_column(String(32), nullable=False)
    comment_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False
    )  # the bot's brief; the UI puts the buttons under it
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    inactive_days: Mapped[float] = mapped_column(Float, nullable=False)
    changes: Mapped[list[str]] = mapped_column(JSONB, nullable=False)


class AlertDecision(Base):
    """Append-only log of human decisions. An alert's current state is derived from its last row."""

    __tablename__ = "alert_decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    work_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alerts.work_item_id", ondelete="CASCADE"), nullable=False, index=True
    )
    event: Mapped[str] = mapped_column(String(16), nullable=False)  # approve | reject | undo
    decided_by: Mapped[str] = mapped_column(String(255), nullable=False)
    prev_priority: Mapped[str | None] = mapped_column(String(16))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
