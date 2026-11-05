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
from app.schemas.alert import AlertIn, AlertRead, DecisionIn
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
    return AlertRead(
        **AlertIn.model_validate(alert, from_attributes=True).model_dump(),
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
    project, previous = str(alert.project_id), None
    if body.decision == "approve":
        previous = plane.get_work_item(project, str(work_item_id))["priority"]
        plane.update_work_item(
            project, str(work_item_id), {"priority": "high"}
        )  # Plane first: a failure leaves it pending
        text = (
            f"{by} đã duyệt: độ ưu tiên đổi từ {previous} thành high. "
            "Có thể hoàn tác ngay trên issue."
        )
    else:
        text = f"{by} đã bỏ qua cảnh báo rủi ro này. Có thể mở lại ngay trên issue."
    plane.add_comment(project, str(work_item_id), f"<p>{text}</p>")
    db.add(
        AlertDecision(
            work_item_id=work_item_id, event=body.decision, decided_by=by, prev_priority=previous
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
    if state == "approved":
        plane.update_work_item(project, str(work_item_id), {"priority": last.prev_priority})
        text = f"{by} đã hoàn tác: độ ưu tiên trở lại {last.prev_priority}."
    else:
        text = f"{by} đã mở lại cảnh báo rủi ro này."
    plane.add_comment(project, str(work_item_id), f"<p>{text}</p>")
    db.add(AlertDecision(work_item_id=work_item_id, event="undo", decided_by=by))
    db.commit()
    return read_model(db, alert)
