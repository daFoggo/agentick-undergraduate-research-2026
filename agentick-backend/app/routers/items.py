from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.item import Item
from app.schemas.error import ErrorDetail
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.schemas.pagination import FindResult

router = APIRouter(prefix="/items", tags=["items"])

NOT_FOUND_RESPONSE = {404: {"model": ErrorDetail, "description": "Item not found."}}
DUPLICATE_RESPONSE = {
    409: {"model": ErrorDetail, "description": "An item with this name already exists."}
}

# Postgres `integer` columns cap at 2^31-1; bound path/query params so out-of-range
# input is a 422 instead of a 500 DataError from the database.
ItemId = Annotated[int, Path(ge=1, le=2_147_483_647)]
MAX_PAGE = 1_000_000


def get_existing_item(item_id: ItemId, db: Annotated[Session, Depends(get_db)]) -> Item:
    """Shared "load or 404" dependency for routes that take an item_id path param."""
    item = db.get(Item, item_id)
    if item is None:
        raise NotFoundError(detail="Item not found.")
    return item


# All handlers below use the sync SQLAlchemy `Session` (sync psycopg driver), which
# performs blocking I/O. They are plain `def`, not `async def`, so FastAPI offloads
# each call to its threadpool instead of blocking the event loop for every request.


@router.get("", response_model=FindResult[ItemRead], summary="List items", operation_id="listItems")
def list_items(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1, le=MAX_PAGE)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> FindResult[ItemRead]:
    total_count = db.query(func.count(Item.id)).scalar() or 0
    founds = db.query(Item).order_by(Item.id).offset((page - 1) * page_size).limit(page_size).all()
    return FindResult(founds=founds, total_count=total_count, page=page, page_size=page_size)


@router.post(
    "",
    response_model=ItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an item",
    operation_id="createItem",
    responses=DUPLICATE_RESPONSE,
)
def create_item(item_in: ItemCreate, db: Annotated[Session, Depends(get_db)]) -> Item:
    item = Item(**item_in.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get(
    "/{item_id}",
    response_model=ItemRead,
    summary="Get an item by id",
    operation_id="getItem",
    responses=NOT_FOUND_RESPONSE,
)
def get_item(item: Annotated[Item, Depends(get_existing_item)]) -> Item:
    return item


@router.patch(
    "/{item_id}",
    response_model=ItemRead,
    summary="Update an item",
    operation_id="updateItem",
    responses={**NOT_FOUND_RESPONSE, **DUPLICATE_RESPONSE},
)
def update_item(
    item_in: ItemUpdate,
    item: Annotated[Item, Depends(get_existing_item)],
    db: Annotated[Session, Depends(get_db)],
) -> Item:
    for field, value in item_in.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item",
    operation_id="deleteItem",
    responses=NOT_FOUND_RESPONSE,
)
def delete_item(
    item: Annotated[Item, Depends(get_existing_item)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    db.delete(item)
    db.commit()
