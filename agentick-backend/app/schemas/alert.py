import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Change = Annotated[str, Field(max_length=1000)]


class AlertIn(BaseModel):
    work_item_id: uuid.UUID
    project_id: uuid.UUID
    issue_key: str = Field(max_length=32)
    comment_id: uuid.UUID
    rank: int = Field(ge=1, le=100_000)
    size: int = Field(ge=1, le=100_000)
    score: float
    status: str = Field(max_length=64)
    inactive_days: float = Field(ge=0)
    changes: list[Change] = Field(max_length=10)


class AlertRead(AlertIn):
    model_config = ConfigDict(from_attributes=True)

    state: Literal["pending", "approved", "dismissed"]
    decided_by: str | None


class DecisionIn(BaseModel):
    decision: Literal["approve", "reject"]
