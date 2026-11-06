from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import ChatDep, PlaneDep, PlaneSession
from app.schemas.error import ErrorDetail
from app.services import assistant

router = APIRouter(prefix="/assistant", tags=["assistant"])


class AskIn(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class ToolUse(BaseModel):
    name: str
    arguments: dict
    ok: bool


class AskOut(BaseModel):
    answer: str
    tools: list[ToolUse]  # every lookup the answer rests on
    cost_usd: float
    unverified: bool  # the model named an issue no lookup returned: the answer was replaced


@router.post(
    "/ask",
    response_model=AskOut,
    summary="Ask about delivery risk",
    operation_id="askAssistant",
    responses={
        401: {"model": ErrorDetail, "description": "Not signed in to Plane."},
        403: {"model": ErrorDetail, "description": "Plane refused to list the user's projects."},
        502: {
            "model": ErrorDetail,
            "description": "Plane or the language model could not be reached.",
        },
        503: {"model": ErrorDetail, "description": "The assistant is not configured."},
    },
)
def ask(
    body: AskIn,
    session: PlaneSession,
    plane: PlaneDep,
    chat: ChatDep,
    db: Annotated[Session, Depends(get_db)],
) -> AskOut:
    """One question, one answer. The model may call read-only lookups over the alerts, sprint
    plans and decisions of the projects the signed-in user can see; it cannot change anything."""
    visible = plane.visible_project_ids(session)
    return AskOut(**assistant.ask(db, visible, body.question, chat))
