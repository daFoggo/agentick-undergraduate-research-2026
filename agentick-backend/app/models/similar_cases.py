import uuid

from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SimilarCases(Base, TimestampMixin):
    """Finished cases most similar to one work item, published by the offline job. Read-only."""

    __tablename__ = "similar_cases"

    work_item_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    sizes: Mapped[dict] = mapped_column(
        JSONB, nullable=False
    )  # {small, medium, large} among the 20 nearest cases
    project_size: Mapped[int] = mapped_column(Integer, nullable=False)
    cases: Mapped[list] = mapped_column(
        JSONB, nullable=False
    )  # the few closest cases, shown as examples
