import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Case(BaseModel):
    key: str = Field(max_length=32)
    title: str = Field(max_length=300)
    size: Literal["small", "medium", "large"]  # relative to the project's own story-point scale
    days: float | None = Field(
        ge=0
    )  # time the case spent in progress; None when TAWOS has no value
    path: str = Field(
        pattern=r"^/[\w-]+/browse/[\w-]+/$", max_length=120
    )  # a Plane page: links never leave Plane


class Sizes(BaseModel):
    small: int = Field(ge=0)
    medium: int = Field(ge=0)
    large: int = Field(ge=0)


class SimilarCasesIn(BaseModel):
    work_item_id: uuid.UUID
    project_id: uuid.UUID
    sizes: Sizes
    project_size: int = Field(ge=0)
    cases: list[Case] = Field(max_length=5)

    @model_validator(mode="after")
    def _sizes_add_up_to_something(self):
        if self.sizes.small + self.sizes.medium + self.sizes.large == 0:
            raise ValueError("sizes must count at least one case")
        return self
