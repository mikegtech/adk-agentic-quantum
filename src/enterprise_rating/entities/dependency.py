from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel, Field


class DependencyBase(BaseModel):
    prog_key: str  # Primary key for the program
    revision_key: str  # Revision key for the algorithm
    alg_type: str | None = None  # Type of the algorithm
    category_id: str  # Category ID associated with the algorithm
    description: str  # Description of the algorithm
    date_last_modified: str  # Date when the algorithm was last modified
    index: int  # Index of the algorithm in the sequence
    c_index: int | None = None  # Optional index for the algorithm
    version: str  # Version of the algorithm
    program_id: str  # Program ID associated with the algorithm
    assign_filter: str  # Filter for assignment
    advanced_type: str  # Advanced type of the algorithm
    dependencies: list[Dependency] = Field(default_factory=list, alias="d")

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True


class CalculatedVariable(DependencyBase):
    ib_type: Literal["10"]


class TableVariable(DependencyBase):
    ib_type: Literal["2"]


class ResultVariable(DependencyBase):
    ib_type: Literal["3"]


class InputVariable(DependencyBase):
    ib_type: Literal["4"]


Dependency = Union[CalculatedVariable, TableVariable, ResultVariable, InputVariable]
