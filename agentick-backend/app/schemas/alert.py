import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Change = Annotated[str, Field(max_length=1000)]
# the first three are carried out in Plane on approval; the rest is advice
Cause = Literal[
    "waiting_on_person", "blocked_by_issue", "needs_decision", "unclear_scope", "not_started"
]
ActionType = Literal["raise_priority", "nudge_owner", "assign_owner", "split", "move_next_cycle"]


class AlertIn(BaseModel):
    work_item_id: uuid.UUID
    project_id: uuid.UUID
    issue_key: str = Field(max_length=32)
    comment_id: uuid.UUID
    mark: float = Field(
        default=0.5, ge=0, le=1
    )  # share of the sprint that had passed when it was raised
    rank: int = Field(ge=1, le=100_000)
    size: int = Field(ge=1, le=100_000)
    score: float
    status: str = Field(max_length=64)
    inactive_days: float = Field(ge=0)
    changes: list[Change] = Field(max_length=10)
    action_type: ActionType = "raise_priority"
    action_text: str | None = Field(default=None, max_length=2000)
    cause: Cause | None = None  # why the issue looks stuck, from the agent that read its comments
    evidence_quote: str | None = Field(default=None, max_length=500)  # what it quoted
    cycle_id: uuid.UUID | None = None  # the cycle the item is in now (where an undo puts it back)
    target_cycle_id: uuid.UUID | None = None  # the cycle a move_next_cycle action puts it in

    @model_validator(mode="after")
    def action_needs_its_inputs(self):
        if self.action_type == "nudge_owner" and not self.action_text:
            raise ValueError("a reminder needs its text")
        if self.action_type == "move_next_cycle" and not (self.cycle_id and self.target_cycle_id):
            raise ValueError("a move needs the current and the target cycle")
        return self


class AlertRead(AlertIn):
    model_config = ConfigDict(from_attributes=True)

    state: Literal["pending", "approved", "dismissed"]
    decided_by: str | None


class DecisionIn(BaseModel):
    decision: Literal["approve", "reject"]
