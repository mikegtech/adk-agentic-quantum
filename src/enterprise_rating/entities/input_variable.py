from pydantic import BaseModel


class Input(BaseModel):
    """Represents a input."""

    l: str
    i: str
    p: str
    d: str
    c: str
    sys: str
