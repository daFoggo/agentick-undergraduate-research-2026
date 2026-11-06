import uuid

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Index, Integer, String, func
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
    mark: Mapped[float] = mapped_column(
        Float, nullable=False, server_default="0.5"
    )  # share of the sprint gone
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    inactive_days: Mapped[float] = mapped_column(Float, nullable=False)
    changes: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    action_type: Mapped[str] = mapped_column(
        String(24), nullable=False, server_default="raise_priority"
    )
    action_text: Mapped[str | None] = mapped_column(String(2000))  # the drafted reminder, if any
    cause: Mapped[str | None] = mapped_column(String(24))
    evidence_quote: Mapped[str | None] = mapped_column(String(500))
    assignee_ids: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )  # Plane user ids of the assignees when the alert was published
    diagnosis: Mapped[dict | None] = mapped_column(
        JSONB
    )  # the card: hypotheses + evidence, see schemas.alert
    cycle_id: Mapped[uuid.UUID | None] = mapped_column()  # cycle the item is in now
    target_cycle_id: Mapped[uuid.UUID | None] = mapped_column()  # cycle a move puts it in


class AlertDecision(Base):
    """Append-only log of human decisions. An alert's current state is derived from its last row."""

    __tablename__ = "alert_decisions"
    __table_args__ = (Index("work_item_id_idx", "work_item_id"),)  # the name the migration gave it

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    work_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("alerts.work_item_id", ondelete="CASCADE"), nullable=False
    )
    event: Mapped[str] = mapped_column(String(16), nullable=False)  # approve | reject | undo
    decided_by: Mapped[str] = mapped_column(String(255), nullable=False)
    prev_priority: Mapped[str | None] = mapped_column(String(16))
    applied_comment_id: Mapped[str | None] = mapped_column(String(64))  # the reminder to take back
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
