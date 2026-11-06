import uuid
from contextlib import suppress
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, DuplicatedError, ForbiddenError, NotFoundError
from app.db.session import get_db
from app.dependencies import PlaneDep, PlaneSession, require_ingest_token
from app.models.plan import Plan, PlanDecision, PlanItem
from app.schemas.error import ErrorDetail
from app.schemas.plan import (
    PlanDecisionIn,
    PlanIn,
    PlanItemIn,
    PlanItemRead,
    PlanRead,
    PlanUndoIn,
)

router = APIRouter(prefix="/plans", tags=["plans"])
USER_ERRORS = {
    401: {"model": ErrorDetail, "description": "Not signed in to Plane."},
    403: {"model": ErrorDetail, "description": "Plane does not let this user see the project."},
    502: {"model": ErrorDetail, "description": "Plane could not be reached."},
}
DECIDE_ERRORS = USER_ERRORS | {
    404: {"model": ErrorDetail, "description": "No such plan, or a work item that is not in it."},
    409: {"model": ErrorDetail, "description": "No item is in a state that allows this."},
}
STATE = {None: "pending", "undo": "pending", "approve": "applied", "reject": "dismissed"}


def read_model(db: Session, plan: Plan, errors: dict[uuid.UUID, str] | None = None) -> PlanRead:
    last: dict[uuid.UUID, str] = {}
    log = db.scalars(
        select(PlanDecision).where(PlanDecision.plan_id == plan.id).order_by(PlanDecision.id)
    )
    for row in log:
        last[row.work_item_id] = row.event
    items = [
        PlanItemRead(
            **PlanItemIn.model_validate(item).model_dump(), state=STATE[last.get(item.work_item_id)]
        )
        for item in plan.items
    ]
    head = PlanIn.model_validate(plan).model_dump(exclude={"items"})
    return PlanRead(**head, id=plan.id, items=items, errors=errors or {})


@router.put(
    "",
    summary="Publish the plan of a sprint",
    operation_id="publishPlan",
    dependencies=[Depends(require_ingest_token)],
    responses={
        401: {"model": ErrorDetail, "description": "Missing or wrong ingest token."},
        409: {"model": ErrorDetail, "description": "A person already decided on this plan."},
    },
)
def publish(body: PlanIn, db: Annotated[Session, Depends(get_db)]) -> dict[str, int]:
    """A new run replaces the plan of the same cycle, unless people already decided on it."""
    old = db.scalars(select(Plan).where(Plan.cycle_id == body.cycle_id).with_for_update()).first()
    if old:
        if db.scalars(select(PlanDecision.id).where(PlanDecision.plan_id == old.id)).first():
            raise DuplicatedError("A person already decided on this plan; it is kept.")
        db.delete(old)
        db.flush()
    fields = body.model_dump(exclude={"items"})
    db.add(
        Plan(
            **fields,
            items=[PlanItem(position=i, **item.model_dump()) for i, item in enumerate(body.items)],
        )
    )
    db.commit()
    return {"stored": len(body.items)}


@router.get(
    "",
    response_model=list[PlanRead],
    summary="Plans of the projects the signed-in user can see",
    operation_id="listPlans",
    responses=USER_ERRORS,
)
def list_plans(
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
    cycle_id: Annotated[uuid.UUID | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> list[PlanRead]:
    visible = plane.visible_project_ids(session)
    query = select(Plan).where(Plan.project_id.in_(visible))
    if cycle_id:
        query = query.where(Plan.cycle_id == cycle_id)
    plans = db.scalars(query.order_by(Plan.created_at.desc()).limit(limit)).all()
    return [read_model(db, p) for p in plans]


def locked_plan(db: Session, plane: PlaneDep, session: str, plan_id: uuid.UUID) -> tuple[Plan, str]:
    """The plan, locked until commit (concurrent deciders go one by one), and the user's name."""
    by = plane.user_name(session)
    plan = db.scalars(select(Plan).where(Plan.id == plan_id).with_for_update()).first()
    if plan is None:
        raise NotFoundError("No such plan.")
    if str(plan.project_id) not in plane.visible_project_ids(session):
        raise ForbiddenError()
    return plan, by


def targets(
    plan: Plan, state: PlanRead, ids: list[uuid.UUID] | None, wanted: tuple[str, ...]
) -> list[PlanItem]:
    """Items to act on: those named (all if none) that are in one of the `wanted` states."""
    in_plan = {item.work_item_id: item for item in plan.items}
    if ids and (unknown := set(ids) - set(in_plan)):
        raise NotFoundError(f"Not in this plan: {sorted(map(str, unknown))[0]}.")
    current = {i.work_item_id: i.state for i in state.items}
    chosen = [w for w in (ids or list(in_plan)) if current[w] in wanted]
    if not chosen:
        raise DuplicatedError(f"No item is {' or '.join(wanted)}.")
    return [in_plan[w] for w in chosen]


def log(db: Session, plan: Plan, item: PlanItem, event: str, by: str) -> None:
    db.add(
        PlanDecision(plan_id=plan.id, work_item_id=item.work_item_id, event=event, decided_by=by)
    )
    db.commit()  # one item at a time: what Plane already did is never lost to a later failure


def note(plane: PlaneDep, plan: Plan, item: PlanItem, text: str) -> None:
    with suppress(AppError):  # the move is done; a missing comment must not undo it
        plane.add_comment(str(plan.project_id), str(item.work_item_id), f"<p>{text}</p>")


@router.post(
    "/{plan_id}/decision",
    response_model=PlanRead,
    summary="Approve or dismiss items of a plan",
    operation_id="decidePlan",
    responses=DECIDE_ERRORS,
)
def decide(
    plan_id: uuid.UUID,
    body: PlanDecisionIn,
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
) -> PlanRead:
    """Approve moves each chosen item to the next cycle; an item Plane refuses stays pending."""
    plan, by = locked_plan(db, plane, session, plan_id)
    errors: dict[uuid.UUID, str] = {}
    for item in targets(plan, read_model(db, plan), body.work_item_ids, ("pending",)):
        if body.decision == "approve":
            try:
                plane.move_to_cycle(
                    str(plan.project_id), str(item.work_item_id), str(plan.next_cycle_id)
                )
            except AppError as exc:
                errors[item.work_item_id] = str(exc.detail)
                continue
            note(plane, plan, item, f"{by} approved the sprint plan: moved to the next cycle.")
            log(db, plan, item, "approve", by)
        else:
            log(db, plan, item, "reject", by)
    return read_model(db, plan, errors)


@router.post(
    "/{plan_id}/undo",
    response_model=PlanRead,
    summary="Undo decisions on items of a plan",
    operation_id="undoPlan",
    responses=DECIDE_ERRORS,
)
def undo(
    plan_id: uuid.UUID,
    body: PlanUndoIn,
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
) -> PlanRead:
    """A moved item goes back to its cycle (if Plane refuses, it stays moved)."""
    plan, by = locked_plan(db, plane, session, plan_id)
    state = read_model(db, plan)
    was = {i.work_item_id: i.state for i in state.items}
    errors: dict[uuid.UUID, str] = {}
    for item in targets(plan, state, body.work_item_ids, ("applied", "dismissed")):
        if was[item.work_item_id] == "applied":
            try:
                plane.move_to_cycle(
                    str(plan.project_id), str(item.work_item_id), str(plan.cycle_id)
                )
            except AppError as exc:
                errors[item.work_item_id] = str(exc.detail)
                continue
            note(plane, plan, item, f"{by} undid the sprint plan: the item is back in its cycle.")
        log(db, plan, item, "undo", by)
    return read_model(db, plan, errors)
