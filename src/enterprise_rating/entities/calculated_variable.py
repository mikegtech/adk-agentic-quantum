from pydantic import BaseModel


class CalculatedVariable(BaseModel):
    """Represents a calculated variable in the program version."""

    name: str
    description: str
    expression: str
    data_type: str
    is_active: bool = True

    class Config:
        """Pydantic configuration."""

        orm_mode = True  # Enable ORM mode for compatibility with ORMs like SQLAlchemy
        allow_population_by_field_name = True  # Allow population by field names
