from pydantic import BaseModel


class Category(BaseModel):
    """Represents a category."""

    l: str
    i: str
    dt: str
    d: str
    qt: str
