import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.dependencies import PlaneDep, PlaneSession, require_ingest_token
from app.models.similar_cases import SimilarCases
from app.schemas.error import ErrorDetail
from app.schemas.similar_cases import SimilarCasesIn

router = APIRouter(prefix="/cases", tags=["cases"])

READ_ERRORS = {
    401: {"model": ErrorDetail, "description": "Not signed in to Plane."},
    403: {"model": ErrorDetail, "description": "Plane does not let this user see the work item."},
    404: {"model": ErrorDetail, "description": "No similar cases for this work item."},
    502: {"model": ErrorDetail, "description": "Plane could not be reached."},
}


@router.put(
    "",
    summary="Publish similar cases",
    operation_id="publishSimilarCases",
    dependencies=[Depends(require_ingest_token)],
    responses={401: {"model": ErrorDetail, "description": "Missing or wrong ingest token."}},
)
def publish(body: list[SimilarCasesIn], db: Annotated[Session, Depends(get_db)]) -> dict[str, int]:
    if body:
        rows = [item.model_dump(mode="json") for item in body]
        stmt = insert(SimilarCases).values(rows)
        update = {c: stmt.excluded[c] for c in ("project_id", "sizes", "project_size", "cases")}
        db.execute(stmt.on_conflict_do_update(index_elements=["work_item_id"], set_=update))
        db.commit()
    return {"stored": len(body)}


@router.get(
    "/{work_item_id}",
    response_model=SimilarCasesIn,
    summary="Similar cases of a work item",
    operation_id="getSimilarCases",
    responses=READ_ERRORS,
)
def read(
    work_item_id: uuid.UUID,
    session: PlaneSession,
    plane: PlaneDep,
    db: Annotated[Session, Depends(get_db)],
) -> SimilarCases:
    plane.user_name(session)  # 401 when Plane does not know this session
    found = db.get(SimilarCases, work_item_id)
    if found is None:
        raise NotFoundError("No similar cases for this work item.")
    plane.assert_can_view(session, str(found.project_id), str(work_item_id))
    return found
