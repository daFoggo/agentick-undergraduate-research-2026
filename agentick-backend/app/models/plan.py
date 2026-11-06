import uuid

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Plan(Base, TimestampMixin):
    """A sprint-level plan from the offline job: which open issues move to the next cycle."""

    __tablename__ = "plans"
    __table_args__ = (UniqueConstraint("cycle_id"),)  # a cycle has one plan; a new run replaces it

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    cycle_id: Mapped[uuid.UUID] = mapped_column(nullable=False)  # the sprint the plan is about
    next_cycle_id: Mapped[uuid.UUID] = mapped_column(nullable=False)  # where moved items go
    sprint_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mark: Mapped[float] = mapped_column(Float, nullable=False)  # share of the sprint gone
    open_count: Mapped[int] = mapped_column(Integer, nullable=False)
    history_sprints: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # earlier sprints behind the share
    unfinished_share: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # of open issues, in those sprints
    expected_unfinished: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # share x open issues now
    budget: Mapped[int] = mapped_column(Integer, nullable=False)  # expected_unfinished, rounded
    items: Mapped[list["PlanItem"]] = relationship(
        cascade="all, delete-orphan", order_by="PlanItem.position"
    )


class PlanItem(Base):
    __tablename__ = "plan_items"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plans.id", ondelete="CASCADE"), primary_key=True
    )
    work_item_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    issue_key: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    why: Mapped[str] = mapped_column(String(16), nullable=False)  # risk | follows
    cause: Mapped[str | None] = mapped_column(String(24))  # top cause of the issue's diagnosis
    reason: Mapped[str | None] = mapped_column(String(400))  # and its one-sentence reason


class PlanDecision(Base):
    """Append-only decisions on plan items; an item's state is its last row (undo = pending)."""

    __tablename__ = "plan_decisions"
    __table_args__ = (Index("plan_decisions_item_idx", "plan_id", "work_item_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plans.id", ondelete="CASCADE"), nullable=False
    )
    work_item_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    event: Mapped[str] = mapped_column(String(16), nullable=False)  # approve | reject | undo
    decided_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
