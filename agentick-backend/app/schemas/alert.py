import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Change = Annotated[str, Field(max_length=1000)]
# the first three are carried out in Plane on approval; the rest is advice
Cause = Literal[  # the first five are the earlier labels, kept so stored alerts still read
    "waiting_on_person",
    "blocked_by_issue",
    "needs_decision",
    "unclear_scope",
    "not_started",
    "pulled_away",
    "blocked",
    "waiting_person",
    "carry_over",
]
ActionType = Literal["raise_priority", "nudge_owner", "assign_owner", "split", "move_next_cycle"]


class Evidence(BaseModel):
    id: str = Field(max_length=64)
    kind: Literal["discussion", "owner", "blockers", "sprint", "history"]
    ts: str = Field(max_length=40)
    text: str = Field(max_length=1000)
    ref_key: str | None = Field(default=None, max_length=32)  # another issue this event is about
    safe_text: str | None = Field(
        default=None, max_length=300
    )  # what a viewer outside its project sees


class Hypothesis(BaseModel):
    cause: Cause
    label: str = Field(max_length=100)
    reason: str = Field(max_length=400)
    evidence: list[Evidence] = Field(min_length=1, max_length=12)


class DiagnosisAction(BaseModel):
    type: ActionType | None = None
    text: str | None = Field(default=None, max_length=2000)


class Note(BaseModel):
    kind: Literal["sprint_overload", "done_not_updated"]
    text: str = Field(max_length=300)
    event_ids: list[str] = Field(default=[], max_length=12)


class DiagnosisMeta(BaseModel):
    model: str = Field(max_length=100)
    cost: float = Field(ge=0)  # USD of the one model call
    error: str | None = Field(default=None, max_length=200)  # why the call or its reply failed


class Diagnosis(BaseModel):
    hypotheses: list[Hypothesis] = Field(max_length=3)
    dropped: int = Field(default=0, ge=0, le=100)  # hypotheses the verifier removed
    unknown: bool
    missing_info: str | None = Field(default=None, max_length=300)
    action: DiagnosisAction = DiagnosisAction()
    meta: DiagnosisMeta | None = None  # what the model call cost and whether it failed
    notes: list[Note] = Field(
        default=[], max_length=2
    )  # states beside the diagnosis, about this issue's own sprint


def prefix(key: str) -> str:
    return key.rsplit("-", 1)[0]


def redact(diagnosis: Diagnosis, issue_key: str) -> Diagnosis:
    """Evidence about an issue of another project shows only its safe summary (priority, state).

    The model's own words about it (reason, missing_info) could repeat its text, so they fall back
    to the label."""
    hidden = False
    for h in diagnosis.hypotheses:
        cut = False
        for e in h.evidence:
            if e.ref_key and prefix(e.ref_key) != prefix(issue_key):
                e.text, e.ref_key, cut = e.safe_text or "an issue in another project", None, True
        if cut:
            h.reason, hidden = h.label, True
    if hidden:
        diagnosis.missing_info = None
    return diagnosis


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
    assignee_ids: list[uuid.UUID] = Field(default=[], max_length=20)
    diagnosis: Diagnosis | None = None  # why it is at risk: hypotheses with evidence, or "unknown"
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
