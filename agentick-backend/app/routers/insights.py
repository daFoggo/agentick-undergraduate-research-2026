import uuid
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import PlaneDep, PlaneSession
from app.models.alert import Alert, AlertDecision
from app.schemas.alert import AlertIn, redact
from app.schemas.error import ErrorDetail
from app.schemas.insights import (
    ActionRow,
    AiStats,
    CauseRow,
    Counts,
    DayRow,
    PendingItem,
    ProjectRow,
    Summary,
)

router = APIRouter(prefix="/insights", tags=["insights"])
STATES = {"approve": "approved", "reject": "dismissed"}
ERRORS = {
    401: {"model": ErrorDetail, "description": "Not signed in to Plane."},
    403: {"model": ErrorDetail, "description": "Plane refused to list the user's projects."},
    502: {"model": ErrorDetail, "description": "Plane could not be reached."},
}
DAYS = 30


def states(db: Session, project_ids: list[str]) -> list[tuple[Alert, str]]:
    """Alerts of the given projects with their state (last decision event; undo means pending).

    shortcut: aggregated in Python, fine for thousands of alerts; use SQL group-by at millions."""
    alerts = db.scalars(select(Alert).where(Alert.project_id.in_(project_ids))).all()
    last: dict = {}
    for ev in db.scalars(
        select(AlertDecision)
        .where(AlertDecision.work_item_id.in_([a.work_item_id for a in alerts]))
        .order_by(AlertDecision.id)
    ):
        last[ev.work_item_id] = ev.event
    return [(a, STATES.get(last.get(a.work_item_id), "pending")) for a in alerts]


def tally(counts: Counts, state: str) -> None:
    counts.total += 1
    setattr(counts, state, getattr(counts, state) + 1)


@router.get(
    "/summary",
    response_model=Summary,
    summary="Statistics of the alerts and the AI diagnosis",
    operation_id="getInsightsSummary",
    responses=ERRORS,
)
def summary(
    session: PlaneSession, plane: PlaneDep, db: Annotated[Session, Depends(get_db)]
) -> Summary:
    """Counted over the projects Plane lets the caller see, never another team's alerts."""
    rows = states(db, plane.visible_project_ids(session))
    total, causes, actions, projects = Counts(), Counter(), defaultdict(Counts), defaultdict(Counts)
    kept = dropped = diagnosed = unknown = failed = 0
    notes, kinds, models, cost = Counter(), Counter(), Counter(), 0.0
    for alert, state in rows:
        tally(total, state)
        tally(
            actions.setdefault(alert.action_type, ActionRow(action_type=alert.action_type)), state
        )
        tally(projects.setdefault(alert.project_id, ProjectRow(project_id=alert.project_id)), state)
        d = alert.diagnosis
        top = d["hypotheses"][0]["cause"] if d and d.get("hypotheses") else None
        causes[top or alert.cause or ("unknown" if d else "undiagnosed")] += 1
        if not d:
            continue
        diagnosed += 1
        unknown += bool(d.get("unknown"))
        kept += len(d.get("hypotheses", []))
        dropped += d.get("dropped", 0)
        notes.update(n["kind"] for n in d.get("notes", []))
        kinds.update(e["kind"] for h in d.get("hypotheses", []) for e in h["evidence"])
        if m := d.get("meta"):
            cost += m["cost"]
            failed += bool(m.get("error"))
            models[m["model"]] += 1
    decided = total.approved + total.dismissed
    since = datetime.now(UTC) - timedelta(days=DAYS)
    by_day: dict[str, DayRow] = {}
    visible = [a.work_item_id for a, _ in rows]
    undone = db.scalar(
        select(func.count()).where(
            AlertDecision.event == "undo", AlertDecision.work_item_id.in_(visible)
        )
    )
    for ev in db.scalars(
        select(AlertDecision).where(
            AlertDecision.work_item_id.in_(visible), AlertDecision.created_at >= since
        )
    ):
        day = ev.created_at.date().isoformat()
        row = by_day.setdefault(day, DayRow(day=day))
        setattr(row, ev.event, getattr(row, ev.event) + 1)
    return Summary(
        alerts=total,
        acceptance_rate=total.approved / decided if decided else None,
        undone=undone,
        causes=[CauseRow(cause=c, n=n) for c, n in causes.most_common()],
        actions=sorted(actions.values(), key=lambda r: -r.total),
        ai=AiStats(
            diagnosed=diagnosed,
            unknown=unknown,
            hypotheses_kept=kept,
            hypotheses_dropped=dropped,
            notes=dict(notes),
            evidence_kinds=dict(kinds),
            cost_usd=round(cost, 5),
            calls_failed=failed,
            models=dict(models),
        ),
        projects=sorted(projects.values(), key=lambda r: -r.total),
        decisions_by_day=sorted(by_day.values(), key=lambda r: r.day),
    )


@router.get(
    "/pending",
    response_model=list[PendingItem],
    summary="Alerts waiting for a decision, highest score first",
    operation_id="listPendingAlerts",
    responses=ERRORS,
)
def pending(
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
    limit: int = 20,
    assignee: uuid.UUID | None = None,
) -> list[PendingItem]:
    """assignee: only work items assigned to this Plane user (the "Your work" list)."""
    waiting = [
        a
        for a, s in states(db, plane.visible_project_ids(session))
        if s == "pending" and (assignee is None or str(assignee) in a.assignee_ids)
    ]
    out = []
    for a in sorted(waiting, key=lambda a: -a.score)[: max(1, min(limit, 100))]:
        top = None
        if a.diagnosis:
            d = redact(AlertIn.model_validate(a, from_attributes=True).diagnosis, a.issue_key)
            top = d.hypotheses[0] if d.hypotheses else None
        out.append(
            PendingItem(
                work_item_id=a.work_item_id,
                project_id=a.project_id,
                issue_key=a.issue_key,
                score=a.score,
                rank=a.rank,
                size=a.size,
                action_type=a.action_type,
                diagnosed=bool(a.diagnosis),
                cause_label=top.label if top else None,
                reason=top.reason if top else None,
            )
        )
    return out
