from pydantic import BaseModel


class FindResult[T](BaseModel):
    founds: list[T]
    total_count: int
    page: int
    page_size: int
