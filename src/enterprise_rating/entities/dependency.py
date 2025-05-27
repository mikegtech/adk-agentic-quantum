from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel


class DependencyBase(BaseModel):
    prog_key: str  # Primary key for the program
    revision_key: str  # Revision key for the algorithm
    alg_type: str | None = None  # Type of the algorithm
    category_id: str  # Category ID associated with the algorithm
    description: str  # Description of the algorithm
    date_last_modified: str  # Date when the algorithm was last modified
    index: int  # Index of the algorithm in the sequence
    custom_id: int | None = None  # Optional index for the algorithm
    version: str  # Version of the algorithm
    program_id: str  # Program ID associated with the algorithm
    universal: str = "0"  # Universal flag for the algorithm
    data_type: str | None = None  # Data type of the algorithm
    ib_type: str | None = None  # IB type of the algorithm
    level_id: str | None = None  # Level ID for the algorithm
    processed: str | None = None  # Processed flag for the algorithm
    # dependency_vars: list[Dependency]
    dependency_vars: dict[str, Dependency] | None = None

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True


class CalculatedVariable(DependencyBase):
    ib_type: Literal["10"]


class TableVariable(DependencyBase):
    ib_type: Literal["6", "9"]


class ResultVariable(DependencyBase):
    ib_type: Literal["8"]


class InputVariable(DependencyBase):
    ib_type: Literal["4"]


Dependency = Union[CalculatedVariable, TableVariable, ResultVariable, InputVariable]
