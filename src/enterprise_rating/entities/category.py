from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Category(BaseModel):
    """
    Represents a category.
    """
    l: str
    i: str
    dt: str
    d: str
    qt: str
