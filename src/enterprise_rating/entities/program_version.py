from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from enterprise_rating.entities.category import Category
from enterprise_rating.entities.input_variable import Input


class IbSchema(BaseModel):
    """
    Represents a insbridge schema.
    """
    categories: List[Category]
    inputs: List[Input]


class ProgramVersion(BaseModel):
    """
    Represents a program_version.
    """
    sub: str
    line: int
    ib_schema: IbSchema
    prog: int
    ver: str
    verName: str
    pk: str
    gpk: str
    ed: str
    ed_exact: str
    persisted: bool
    date_mask: str
    culture: str
    decimal_symbol: str
    group_symbol: str
    model_config = ConfigDict(from_attributes=True)

