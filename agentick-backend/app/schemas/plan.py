import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.alert import Cause


class PlanItemIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    work_item_id: uuid.UUID
    issue_key: str = Field(max_length=32)
    score: float = Field(ge=0, le=1)
    why: Literal[
        "risk", "follows"
    ]  # follows: it waits on a moved issue, so it cannot finish either
    cause: Cause | None = None
    reason: str | None = Field(default=None, max_length=400)


class PlanIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: uuid.UUID
    cycle_id: uuid.UUID
    next_cycle_id: uuid.UUID
    sprint_name: str = Field(max_length=255)
    mark: float = Field(ge=0, le=1)
    open_count: int = Field(ge=1)
    history_sprints: int = Field(ge=1)
    unfinished_share: float = Field(ge=0, le=1)
    expected_unfinished: float = Field(ge=0)
    budget: int = Field(ge=1)
    items: list[PlanItemIn] = Field(min_length=1, max_length=200)


class PlanItemRead(PlanItemIn):
    state: Literal["pending", "applied", "dismissed"]


class PlanRead(PlanIn):
    id: uuid.UUID
    items: list[PlanItemRead]  # type: ignore[assignment]  # the same items, now with their state
    errors: dict[uuid.UUID, str] = {}  # items a request could not move, with Plane's answer


class PlanDecisionIn(BaseModel):
    decision: Literal["approve", "reject"]
    work_item_ids: list[uuid.UUID] | None = Field(
        default=None, max_length=200
    )  # none: every item that is still pending


class PlanUndoIn(BaseModel):
    work_item_ids: list[uuid.UUID] | None = Field(
        default=None, max_length=200
    )  # none: every item that was approved or dismissed
