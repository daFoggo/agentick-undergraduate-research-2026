import html
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicatedError, NotFoundError
from app.db.session import get_db
from app.dependencies import PlaneDep, PlaneSession, require_ingest_token
from app.models.alert import Alert, AlertDecision
from app.schemas.alert import AlertIn, AlertRead, DecisionIn, redact
from app.schemas.error import ErrorDetail

router = APIRouter(prefix="/alerts", tags=["alerts"])

STATES = {"approve": "approved", "reject": "dismissed"}
USER_ERRORS = {
    401: {"model": ErrorDetail, "description": "Not signed in to Plane."},
    403: {"model": ErrorDetail, "description": "Plane does not let this user see the work item."},
    404: {"model": ErrorDetail, "description": "No alert for this work item."},
    502: {"model": ErrorDetail, "description": "Plane could not be reached or refused the change."},
}
CONFLICT = {
    409: {"model": ErrorDetail, "description": "The alert is not in a state that allows this."}
}


def last_event(db: Session, work_item_id: uuid.UUID) -> AlertDecision | None:
    return db.scalars(
        select(AlertDecision)
        .where(AlertDecision.work_item_id == work_item_id)
        .order_by(AlertDecision.id.desc())
        .limit(1)
    ).first()


def read_model(db: Session, alert: Alert) -> AlertRead:
    last = last_event(db, alert.work_item_id)
    state = "pending" if last is None or last.event == "undo" else STATES[last.event]
    data = AlertIn.model_validate(alert, from_attributes=True)
    if data.diagnosis:
        redact(data.diagnosis, alert.issue_key)  # the viewer's own project is checked by authorize()
    return AlertRead(
        **data.model_dump(),
        state=state,
        decided_by=last.decided_by if state != "pending" else None,
    )


def authorize(
    db: Session, plane: PlaneDep, session: str, work_item_id: uuid.UUID, lock: bool = False
) -> tuple[Alert, str]:
    """The caller needs a Plane session that may see this work item. Returns (alert, user name).

    lock=True holds a row lock until commit: two people deciding at once go one by one."""
    by = plane.user_name(session)
    query = select(Alert).where(Alert.work_item_id == work_item_id)
    alert = db.scalars(query.with_for_update() if lock else query).first()
    if alert is None:
        raise NotFoundError("No alert for this work item.")
    plane.assert_can_view(session, str(alert.project_id), str(work_item_id))
    return alert, by


@router.put(
    "",
    summary="Publish alerts",
    operation_id="publishAlerts",
    dependencies=[Depends(require_ingest_token)],
    responses={401: {"model": ErrorDetail, "description": "Missing or wrong ingest token."}},
)
def publish(body: list[AlertIn], db: Annotated[Session, Depends(get_db)]) -> dict[str, int]:
    if body:
        rows = [item.model_dump(mode="json") for item in body]
        stmt = insert(Alert).values(rows)
        update = {c: stmt.excluded[c] for c in rows[0] if c != "work_item_id"}
        db.execute(stmt.on_conflict_do_update(index_elements=["work_item_id"], set_=update))
        db.commit()
    return {"stored": len(body)}


@router.delete(
    "/{work_item_id}",
    status_code=204,
    summary="Retire an alert nobody decided on",
    operation_id="retireAlert",
    dependencies=[Depends(require_ingest_token)],
    responses={
        401: {"model": ErrorDetail, "description": "Missing or wrong ingest token."},
        409: {"model": ErrorDetail, "description": "A person already decided on this alert."},
    },
)
def retire(work_item_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> None:
    """The offline job drops an alert that stopped being valid (the issue was cancelled, say).
    A decision is evaluation data, so an alert somebody approved or dismissed is kept."""
    alert = db.scalars(
        select(Alert).where(Alert.work_item_id == work_item_id).with_for_update()
    ).first()
    if alert is None:
        return
    if last_event(db, work_item_id) is not None:
        raise DuplicatedError("A person already decided on this alert; it is kept.")
    db.delete(alert)
    db.commit()


@router.get(
    "/{work_item_id}",
    response_model=AlertRead,
    summary="Alert of a work item",
    operation_id="getAlert",
    responses=USER_ERRORS,
)
def read(
    work_item_id: uuid.UUID,
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
) -> AlertRead:
    alert, _ = authorize(db, plane, session, work_item_id)
    return read_model(db, alert)


@router.post(
    "/{work_item_id}/decision",
    response_model=AlertRead,
    summary="Approve or dismiss an alert",
    operation_id="decideAlert",
    responses=USER_ERRORS | CONFLICT,
)
def decide(
    work_item_id: uuid.UUID,
    body: DecisionIn,
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
) -> AlertRead:
    alert, by = authorize(db, plane, session, work_item_id, lock=True)
    if read_model(db, alert).state != "pending":
        raise DuplicatedError("This alert already has a decision. Undo it first.")
    project, previous, applied = str(alert.project_id), None, None
    if body.decision == "approve":
        if alert.action_type == "raise_priority":
            previous = plane.get_work_item(project, str(work_item_id))["priority"]
            plane.update_work_item(
                project, str(work_item_id), {"priority": "high"}
            )  # Plane first: a failure leaves it pending
            text = (
                f"{by} approved: priority changed from {previous} to high. "
                "It can be undone on the item."
            )
        elif alert.action_type == "nudge_owner":
            sent = plane.add_comment(
                project, str(work_item_id), f"<p>{html.escape(alert.action_text or '')}</p>"
            )
            applied = sent["id"]
            text = f"{by} approved: the reminder above was posted. It can be undone on the item."
        elif alert.action_type == "move_next_cycle":
            plane.move_to_cycle(project, str(work_item_id), str(alert.target_cycle_id))
            text = f"{by} approved: the item was moved to the next cycle. It can be undone."
        else:
            text = f"{by} accepted the suggestion ({alert.action_type.replace('_', ' ')})."
    else:
        text = f"{by} dismissed this risk alert. It can be reopened on the item."
    plane.add_comment(project, str(work_item_id), f"<p>{text}</p>")
    db.add(
        AlertDecision(
            work_item_id=work_item_id,
            event=body.decision,
            decided_by=by,
            prev_priority=previous,
            applied_comment_id=applied,
        )
    )
    db.commit()
    return read_model(db, alert)


@router.post(
    "/{work_item_id}/undo",
    response_model=AlertRead,
    summary="Undo the decision on an alert",
    operation_id="undoAlert",
    responses=USER_ERRORS | CONFLICT,
)
def undo(
    work_item_id: uuid.UUID,
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
) -> AlertRead:
    alert, by = authorize(db, plane, session, work_item_id, lock=True)
    state = read_model(db, alert).state
    if state == "pending":
        raise DuplicatedError("Nothing to undo.")
    project, last = str(alert.project_id), last_event(db, work_item_id)
    if state == "approved" and alert.action_type == "raise_priority":
        plane.update_work_item(project, str(work_item_id), {"priority": last.prev_priority})
        text = f"{by} undid it: priority is back to {last.prev_priority}."
    elif state == "approved" and alert.action_type == "nudge_owner":
        plane.delete_comment(project, str(work_item_id), last.applied_comment_id)
        text = f"{by} undid it: the reminder was removed."
    elif state == "approved" and alert.action_type == "move_next_cycle":
        plane.move_to_cycle(
            project, str(work_item_id), str(alert.cycle_id)
        )  # 502 if it has finished
        text = f"{by} undid it: the item is back in its cycle."
    else:
        text = f"{by} reopened this risk alert."
    plane.add_comment(project, str(work_item_id), f"<p>{text}</p>")
    db.add(AlertDecision(work_item_id=work_item_id, event="undo", decided_by=by))
    db.commit()
    return read_model(db, alert)
