import uuid

from pydantic import BaseModel


class Counts(BaseModel):
    total: int = 0
    pending: int = 0
    approved: int = 0
    dismissed: int = 0


class ActionRow(Counts):
    action_type: str


class CauseRow(BaseModel):
    cause: str  # a Cause, or "unknown" when the diagnosis found no supported reason
    n: int


class ProjectRow(Counts):
    project_id: uuid.UUID


class DayRow(BaseModel):
    day: str  # YYYY-MM-DD
    approve: int = 0
    reject: int = 0
    undo: int = 0


class AiStats(BaseModel):
    diagnosed: int  # alerts that carry a diagnosis
    unknown: int  # diagnoses that kept no hypothesis
    hypotheses_kept: int
    hypotheses_dropped: int  # removed by the verifier: no real evidence behind them
    notes: dict[str, int]  # sprint_overload / done_not_updated
    evidence_kinds: dict[str, int]  # what the kept hypotheses cite
    cost_usd: float
    calls_failed: int
    models: dict[str, int]


class Summary(BaseModel):
    alerts: Counts
    acceptance_rate: float | None  # approved / (approved + dismissed); None before any decision
    undone: int  # undo events
    causes: list[CauseRow]
    actions: list[ActionRow]
    ai: AiStats
    projects: list[ProjectRow]
    decisions_by_day: list[DayRow]


class PendingItem(BaseModel):
    work_item_id: uuid.UUID
    project_id: uuid.UUID
    issue_key: str
    score: float
    rank: int
    size: int
    action_type: str
    cause_label: str | None
    reason: str | None
